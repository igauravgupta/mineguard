import json

from agents.retreival_agent import agent as retrieval_agent


class DummyTool:
    def __init__(self, name, results):
        self.name = name
        self.results = results
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        return self.results


def test_retrieve_returns_structured_json(monkeypatch):
    laws_tool = DummyTool(
        "laws",
        [
            {
                "content": "law content",
                "metadata": {"source": "law.pdf"},
                "source": "laws",
                "query_part": "training",
            }
        ],
    )
    policies_tool = DummyTool(
        "policies",
        [
            {
                "content": "policy content",
                "metadata": {"source": "policy.txt"},
                "source": "policies",
                "query_part": "training",
            }
        ],
    )

    monkeypatch.setattr(retrieval_agent, "laws_rag_search", laws_tool)
    monkeypatch.setattr(retrieval_agent, "policies_rag_search", policies_tool)

    agent = retrieval_agent.RetrievalAgent()
    payload = json.loads(agent.retrieve("training", k=2))

    assert payload["query"] == "training"
    assert payload["count"] == 2
    assert {item["source"] for item in payload["results"]} == {"laws", "policies"}


def test_retrieve_splits_long_query(monkeypatch):
    long_query = " " .join(["training requirements"] * 40)

    laws_tool = DummyTool(
        "laws",
        [
            {
                "content": "law content",
                "metadata": {},
                "source": "laws",
                "query_part": "part",
            }
        ],
    )
    policies_tool = DummyTool(
        "policies",
        [
            {
                "content": "policy content",
                "metadata": {},
                "source": "policies",
                "query_part": "part",
            }
        ],
    )

    monkeypatch.setattr(retrieval_agent, "laws_rag_search", laws_tool)
    monkeypatch.setattr(retrieval_agent, "policies_rag_search", policies_tool)

    agent = retrieval_agent.RetrievalAgent()
    payload = json.loads(agent.retrieve(long_query, k=1))

    assert len(payload["parts"]) > 1
    assert len(laws_tool.calls) == len(payload["parts"])
    assert len(policies_tool.calls) == len(payload["parts"])


def test_retrieve_truncates_content(monkeypatch):
    long_text = "A" * (retrieval_agent.MAX_CONTENT_CHARS + 50)
    laws_tool = DummyTool(
        "laws",
        [
            {
                "content": long_text,
                "metadata": {},
                "source": "laws",
                "query_part": "training",
            }
        ],
    )
    policies_tool = DummyTool("policies", [])

    monkeypatch.setattr(retrieval_agent, "laws_rag_search", laws_tool)
    monkeypatch.setattr(retrieval_agent, "policies_rag_search", policies_tool)

    agent = retrieval_agent.RetrievalAgent()
    payload = json.loads(agent.retrieve("training", k=1))

    assert payload["results"]
    content = payload["results"][0]["content"]
    assert content.endswith("...")
    assert len(content) <= retrieval_agent.MAX_CONTENT_CHARS + 3
