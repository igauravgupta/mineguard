from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Callable, Iterable, List

from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings

SRC_DIR = Path(__file__).resolve().parents[2]
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from config.constants import Constants
from config.logger import get_logger
from indexing import load_faiss_store


logger = get_logger(__name__)


def _simple_tokenize(text: str) -> List[str]:
	return text.lower().split()


def build_bm25_retriever(
	documents: Iterable[object],
	k: int = 4,
	preprocess_func: Callable[[str], List[str]] | None = _simple_tokenize,
) -> BM25Retriever:
	return BM25Retriever.from_documents(
		list(documents),
		k=k,
		preprocess_func=preprocess_func,
	)


def keyword_search(
	query: str,
	documents: Iterable[object],
	k: int = 4,
) -> List[object]:
	retriever = build_bm25_retriever(documents, k=k)
	return retriever.invoke(query)


def _get_faiss_documents(vector_store) -> List[object]:
	return list(vector_store.docstore._dict.values())


def _doc_key(doc: object) -> str:
	metadata = getattr(doc, "metadata", {})
	page_content = getattr(doc, "page_content", "")
	return f"{page_content}|{metadata}"


def _dedupe_docs(documents: Iterable[object]) -> List[object]:
	seen = set()
	unique_docs = []
	for doc in documents:
		key = _doc_key(doc)
		if key in seen:
			continue
		seen.add(key)
		unique_docs.append(doc)
	return unique_docs


def _cosine_similarity(left: List[float], right: List[float]) -> float:
	dot = sum(a * b for a, b in zip(left, right))
	left_norm = math.sqrt(sum(a * a for a in left))
	right_norm = math.sqrt(sum(b * b for b in right))
	if left_norm == 0 or right_norm == 0:
		return 0.0
	return dot / (left_norm * right_norm)


def rerank_documents(
	query: str,
	documents: List[object],
	embeddings: HuggingFaceEmbeddings,
	top_k: int = 8,
) -> List[object]:
	if not documents:
		return []

	query_vector = embeddings.embed_query(query)
	doc_texts = [doc.page_content for doc in documents]
	doc_vectors = embeddings.embed_documents(doc_texts)
	scored = [
		(doc, _cosine_similarity(query_vector, vector))
		for doc, vector in zip(documents, doc_vectors)
	]
	scored.sort(key=lambda item: item[1], reverse=True)
	return [doc for doc, _ in scored[:top_k]]


def retrieval_pipeline(
	query: str,
	k: int = 4,
	bm25_k: int = 8,
	semantic_k: int = 8,
	rerank_k: int = 8,
	embeddings_dir: str = str(Constants.POLICIES_EMBEDDINGS_DIR),
	model_name: str = Constants.EMBEDDING_MODEL_NAME,
) -> List[object]:
	logger.info("Starting hybrid retrieval")
	embeddings = HuggingFaceEmbeddings(model_name=model_name)
	vector_store = load_faiss_store(embeddings, embeddings_dir)
	documents = _get_faiss_documents(vector_store)
	logger.info("Loaded %d document(s) for retrieval", len(documents))

	bm25_docs = keyword_search(query, documents, k=bm25_k)
	logger.info("BM25 retrieved %d candidate(s)", len(bm25_docs))
	semantic_docs = vector_store.similarity_search(query, k=semantic_k)
	logger.info("Semantic search retrieved %d candidate(s)", len(semantic_docs))
	candidates = _dedupe_docs(bm25_docs + semantic_docs)
	logger.info("Deduped to %d candidate(s)", len(candidates))
	reranked = rerank_documents(query, candidates, embeddings, top_k=rerank_k)
	logger.info("Reranked to %d candidate(s)", len(reranked))
	return reranked[:k]


if __name__ == "__main__":
	logger.info("Running retrieval pipeline")
	results = retrieval_pipeline("training requirements", k=4)
	print(f"Retrieved {len(results)} results.")
	if results:
		print(results[0])
