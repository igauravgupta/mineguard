from langchain_core.documents import Document

from rag.policies_rag import indexing


def test_load_policy_documents_reads_txt(tmp_path):
    policy_path = tmp_path / "policy.txt"
    policy_path.write_text("Safety policy requirements and training", encoding="utf-8")

    docs = indexing.load_policy_documents(policies_dir=tmp_path)

    assert len(docs) == 1
    assert "Safety policy" in docs[0].page_content


def test_filter_noisy_documents_removes_short():
    docs = [
        Document(page_content="policy text" * 10),
        Document(page_content="short"),
    ]

    filtered = indexing.filter_noisy_documents(docs)

    assert len(filtered) == 1
    assert "policy text" in filtered[0].page_content


def test_split_policy_documents_creates_chunks():
    doc = Document(page_content="B" * 120)

    splits = indexing.split_policy_documents(
        [doc],
        chunk_size=50,
        chunk_overlap=10,
        add_start_index=True,
    )

    assert len(splits) >= 2
