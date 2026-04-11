import sys
from pathlib import Path
from typing import List

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

SRC_DIR = Path(__file__).resolve().parents[2]
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from config.constants import Constants
from config.logger import get_logger

logger = get_logger(__name__)


def _iter_policy_paths(policies_dir: Path) -> List[Path]:
	txt_paths = sorted(path for path in policies_dir.rglob("*.txt") if path.is_file())
	logger.info("Discovered %d policy file(s) in %s", len(txt_paths), policies_dir)
	return txt_paths


def _load_policy(path: Path) -> List[object]:
	logger.info("Loading policy: %s", path)
	loader = TextLoader(str(path), encoding="utf-8")
	return loader.load()


def _is_reasonable_text(text: str) -> bool:
	stripped = text.strip()
	if len(stripped) < Constants.MIN_TEXT_LENGTH:
		return False
	printable_chars = sum(1 for ch in stripped if ch.isprintable())
	ascii_chars = sum(1 for ch in stripped if ord(ch) < 128)
	printable_ratio = printable_chars / max(len(stripped), 1)
	ascii_ratio = ascii_chars / max(len(stripped), 1)
	return (
		printable_ratio >= Constants.MIN_PRINTABLE_RATIO
		and ascii_ratio >= Constants.MIN_ASCII_RATIO
	)


def filter_noisy_documents(documents: List[object]) -> List[object]:
	filtered = [doc for doc in documents if _is_reasonable_text(doc.page_content)]
	logger.info("Filtered %d noisy document(s)", len(documents) - len(filtered))
	return filtered


def load_policy_documents(
	policies_dir: Path | str = Constants.POLICIES_DIR,
) -> List[object]:
	policies_path = Path(policies_dir)
	txt_paths = _iter_policy_paths(policies_path)
	if not txt_paths:
		logger.warning("No policy files found under %s", policies_path)
		return []

	documents = []
	for path in txt_paths:
		documents.extend(_load_policy(path))
	logger.info("Loaded %d document(s) from policies", len(documents))
	return documents


def split_policy_documents(
	documents: List[object],
	chunk_size: int = Constants.CHUNK_SIZE,
	chunk_overlap: int = Constants.CHUNK_OVERLAP,
	add_start_index: bool = True,
) -> List[object]:
	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
		add_start_index=add_start_index,
	)
	splits = text_splitter.split_documents(documents)
	logger.info("Split into %d chunk(s)", len(splits))
	return splits


def embed_policy_splits(
	splits: List[object],
	model_name: str = Constants.EMBEDDING_MODEL_NAME,
) -> List[List[float]]:
	embeddings = HuggingFaceEmbeddings(model_name=model_name)
	texts = [doc.page_content for doc in splits]
	return embeddings.embed_documents(texts)


def create_faiss_store(
	splits: List[object],
	embeddings: HuggingFaceEmbeddings,
	output_dir: Path | str = Constants.POLICIES_EMBEDDINGS_DIR,
	batch_size: int = Constants.BATCH_SIZE,
) -> FAISS:
	embedding_dim = len(embeddings.embed_query("hello world"))
	index = faiss.IndexFlatL2(embedding_dim)
	vector_store = FAISS(
		embedding_function=embeddings,
		index=index,
		docstore=InMemoryDocstore(),
		index_to_docstore_id={},
	)
	total = len(splits)
	for start in range(0, total, batch_size):
		batch = splits[start : start + batch_size]
		vector_store.add_documents(documents=batch)
		logger.info("Embedded %d/%d chunk(s)", min(start + batch_size, total), total)

	output_path = Path(output_dir)
	output_path.mkdir(parents=True, exist_ok=True)
	vector_store.save_local(str(output_path))
	logger.info("Saved FAISS index to %s", output_path)
	return vector_store


def load_faiss_store(
	embeddings: HuggingFaceEmbeddings,
	input_dir: Path | str = Constants.POLICIES_EMBEDDINGS_DIR,
) -> FAISS:
	return FAISS.load_local(
		str(input_dir),
		embeddings,
		allow_dangerous_deserialization=True,
	)


def semantic_search(
	query: str,
	embeddings: HuggingFaceEmbeddings,
	input_dir: Path | str = Constants.POLICIES_EMBEDDINGS_DIR,
	k: int = 4,
) -> List[object]:
	vector_store = load_faiss_store(embeddings, input_dir)
	return vector_store.similarity_search(query, k=k)


def build_embeddings_index(
	policies_dir: Path | str = Constants.POLICIES_DIR,
	output_dir: Path | str = Constants.POLICIES_EMBEDDINGS_DIR,
	model_name: str = Constants.EMBEDDING_MODEL_NAME,
	chunk_size: int = Constants.CHUNK_SIZE,
	chunk_overlap: int = Constants.CHUNK_OVERLAP,
	batch_size: int = Constants.BATCH_SIZE,
) -> int:
	logger.info("Starting embeddings index build")
	documents = load_policy_documents(policies_dir)
	documents = filter_noisy_documents(documents)
	splits = split_policy_documents(
		documents,
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
		add_start_index=True,
	)
	embeddings = HuggingFaceEmbeddings(model_name=model_name)
	create_faiss_store(
		splits,
		embeddings,
		output_dir=output_dir,
		batch_size=batch_size,
	)
	logger.info("Embeddings index build complete")
	return len(splits)


if __name__ == "__main__":
	logger.info("Building FAISS index for policy documents")
	split_count = build_embeddings_index()
	print(f"Indexed {split_count} chunks into FAISS.")
