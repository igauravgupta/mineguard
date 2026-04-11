from langchain_core.documents import Document

from rag.laws_rag import indexing


def test_filter_noisy_documents_removes_short():
    docs = [
        Document(page_content="ok text" * 10),
        Document(page_content="short"),
    ]

    filtered = indexing.filter_noisy_documents(docs)

    assert len(filtered) == 1
    assert "ok text" in filtered[0].page_content


def test_split_laws_documents_creates_chunks():
    doc = Document(page_content="A" * 120)

    splits = indexing.split_laws_documents(
        [doc],
        chunk_size=50,
        chunk_overlap=10,
        add_start_index=True,
    )

    assert len(splits) >= 2
