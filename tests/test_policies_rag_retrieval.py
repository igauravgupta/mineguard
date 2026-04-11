from langchain_core.documents import Document

from rag.policies_rag import retreival as policies_retrieval


class DummyEmbeddings:
    def embed_query(self, text: str):
        return [1.0, 0.0] if "training" in text.lower() else [0.0, 1.0]

    def embed_documents(self, texts):
        vectors = []
        for text in texts:
            if "training" in text.lower():
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors


class DummyDocstore:
    def __init__(self, docs):
        self._dict = {str(idx): doc for idx, doc in enumerate(docs)}


class DummyVectorStore:
    def __init__(self, docs, semantic_docs):
        self.docstore = DummyDocstore(docs)
        self._semantic_docs = semantic_docs

    def similarity_search(self, query: str, k: int = 4):
        return self._semantic_docs[:k]


def test_retrieval_pipeline_reranks(monkeypatch):
    docs = [
        Document(page_content="incident reporting process"),
        Document(page_content="training requirements for contractors"),
        Document(page_content="emergency response plan"),
    ]
    semantic_docs = [docs[0], docs[1]]

    def fake_load_faiss_store(embeddings, input_dir):
        return DummyVectorStore(docs, semantic_docs)

    monkeypatch.setattr(policies_retrieval, "load_faiss_store", fake_load_faiss_store)
    monkeypatch.setattr(
        policies_retrieval,
        "HuggingFaceEmbeddings",
        lambda model_name: DummyEmbeddings(),
    )

    results = policies_retrieval.retrieval_pipeline(
        "training",
        k=1,
        bm25_k=3,
        semantic_k=2,
        rerank_k=3,
        embeddings_dir="unused",
        model_name="dummy",
    )

    assert results
    assert "training" in results[0].page_content.lower()
