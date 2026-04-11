import asyncio
import sys
from pathlib import Path
from typing import List

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

SRC_DIR = Path(__file__).resolve().parents[2]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config.constants import Constants
from config.logger import get_logger

logger = get_logger(__name__)


def _iter_pdf_paths(laws_dir: Path) -> List[Path]:
    pdf_paths = sorted(path for path in laws_dir.rglob("*.pdf") if path.is_file())
    logger.info("Discovered %d PDF(s) in %s", len(pdf_paths), laws_dir)
    return pdf_paths


async def _load_pdf(path: Path) -> List[object]:
    logger.info("Loading PDF: %s", path)
    loader = PDFPlumberLoader(str(path))
    return await asyncio.to_thread(loader.load)


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


async def load_laws_pdfs_parallel(
    laws_dir: Path | str = Constants.LAWS_DIR,
    max_concurrency: int = 8,
) -> List[object]:
    laws_path = Path(laws_dir)
    pdf_paths = _iter_pdf_paths(laws_path)
    if not pdf_paths:
        logger.warning("No PDFs found under %s", laws_path)
        return []

    semaphore = asyncio.Semaphore(max_concurrency)

    async def _guarded_load(path: Path) -> List[object]:
        async with semaphore:
            return await _load_pdf(path)

    tasks = [asyncio.create_task(_guarded_load(path)) for path in pdf_paths]
    results = await asyncio.gather(*tasks)
    documents = [doc for batch in results for doc in batch]
    logger.info("Loaded %d document(s) from PDFs", len(documents))
    return documents


def load_laws_pdfs(
    laws_dir: Path | str = Constants.LAWS_DIR,
    max_concurrency: int = 8,
) -> List[object]:
    return asyncio.run(load_laws_pdfs_parallel(laws_dir, max_concurrency))


def split_laws_documents(
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


def embed_laws_splits(
    splits: List[object],
    model_name: str = Constants.EMBEDDING_MODEL_NAME,
) -> List[List[float]]:
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    texts = [doc.page_content for doc in splits]
    return embeddings.embed_documents(texts)


def create_faiss_store(
    splits: List[object],
    embeddings: HuggingFaceEmbeddings,
    output_dir: Path | str = Constants.EMBEDDINGS_DIR,
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
    input_dir: Path | str = Constants.EMBEDDINGS_DIR,
) -> FAISS:
    return FAISS.load_local(
        str(input_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def semantic_search(
    query: str,
    embeddings: HuggingFaceEmbeddings,
    input_dir: Path | str = Constants.EMBEDDINGS_DIR,
    k: int = 4,
) -> List[object]:
    vector_store = load_faiss_store(embeddings, input_dir)
    return vector_store.similarity_search(query, k=k)


def build_embeddings_index(
    laws_dir: Path | str = Constants.LAWS_DIR,
    output_dir: Path | str = Constants.EMBEDDINGS_DIR,
    model_name: str = Constants.EMBEDDING_MODEL_NAME,
    chunk_size: int = Constants.CHUNK_SIZE,
    chunk_overlap: int = Constants.CHUNK_OVERLAP,
    batch_size: int = Constants.BATCH_SIZE,
) -> int:
    logger.info("Starting embeddings index build")
    documents = load_laws_pdfs(laws_dir)
    documents = filter_noisy_documents(documents)
    splits = split_laws_documents(
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
    logger.info("Building FAISS index for laws documents")
    split_count = build_embeddings_index()
    print(f"Indexed {split_count} chunks into FAISS.")
