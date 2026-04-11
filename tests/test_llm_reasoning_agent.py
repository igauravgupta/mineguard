from conftest import DummyResponse, reload_module, reset_llm_singleton


def _setup_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")

    class DummyChatModel:
        last_messages = None

        def __init__(self, model_name: str, api_key: str):
            self.model_name = model_name
            self.api_key = api_key

        def invoke(self, messages):
            DummyChatModel.last_messages = messages
            return DummyResponse("final answer")

    monkeypatch.setattr(llm_module, "ChatLiteLLM", DummyChatModel)
    reset_llm_singleton()
    return DummyChatModel


def test_reasoning_calls_web_search_when_empty(monkeypatch):
    dummy_model = _setup_llm(monkeypatch)
    agent_module = reload_module("agents.llm_reasoning.agent")

    calls = []

    def fake_search(query: str, max_results: int = 5):
        calls.append((query, max_results))
        return [{"title": "Result", "url": "https://example.com", "snippet": "ok"}]

    monkeypatch.setattr(agent_module, "duckduckgo_search", fake_search)

    agent = agent_module.LLMReasoningAgent()
    response = agent.answer("training requirements", {"count": 0, "results": []})

    assert response == "final answer"
    assert calls
    assert dummy_model.last_messages
    user_message = dummy_model.last_messages[1]["content"]
    assert "Retrieval results" in user_message
    assert "Web results" in user_message


def test_reasoning_skips_web_search_when_results(monkeypatch):
    _setup_llm(monkeypatch)
    agent_module = reload_module("agents.llm_reasoning.agent")

    def fail_search(*args, **kwargs):
        raise AssertionError("web search should not be called")

    monkeypatch.setattr(agent_module, "duckduckgo_search", fail_search)

    agent = agent_module.LLMReasoningAgent()
    response = agent.answer("training", {"count": 2, "results": [{"content": "x"}]})

    assert response == "final answer"
