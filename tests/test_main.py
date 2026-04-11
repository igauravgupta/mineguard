import json

from conftest import reload_module


class DummyAgent:
    def detect_intent(self, prompt: str) -> str:
        return "legal query"


class DummyRetrieval:
    def retrieve(self, query: str):
        return json.dumps({"query": query, "results": [], "count": 0})


class DummyReasoning:
    def answer(self, query: str, payload: dict) -> str:
        return "reasoned response"


class DummyAnswer:
    def generate(self, query: str, reasoning: str) -> str:
        return "final response"


def test_main_prints_response(monkeypatch, capsys):
    main_module = reload_module("main")

    monkeypatch.setattr(main_module, "QueryUnderstandAgent", lambda: DummyAgent())
    monkeypatch.setattr(main_module, "RetrievalAgent", lambda: DummyRetrieval())
    monkeypatch.setattr(main_module, "LLMReasoningAgent", lambda: DummyReasoning())
    monkeypatch.setattr(main_module, "AnswerGeneratorAgent", lambda: DummyAnswer())
    main_module.main()

    captured = capsys.readouterr()
    assert "Detected intent: legal query" in captured.out
