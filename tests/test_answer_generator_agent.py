from conftest import DummyResponse, reload_module, reset_llm_singleton


def _setup_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")

    class DummyChatModel:
        def __init__(self, model_name: str, api_key: str):
            self.model_name = model_name
            self.api_key = api_key

        def invoke(self, messages):
            return DummyResponse("unused")

    monkeypatch.setattr(llm_module, "ChatLiteLLM", DummyChatModel)
    reset_llm_singleton()


def test_generate_returns_output(monkeypatch):
    _setup_llm(monkeypatch)
    agent_module = reload_module("agents.answer_generator_agent.agent")

    class DummyAgent:
        last_payload = None

        def invoke(self, payload):
            DummyAgent.last_payload = payload
            return {"output": "final response"}

    monkeypatch.setattr(agent_module, "create_agent", lambda **kwargs: DummyAgent())

    agent = agent_module.AnswerGeneratorAgent()
    response = agent.generate("query", "reasoning")

    assert response == "final response"
    assert DummyAgent.last_payload
    prompt = DummyAgent.last_payload["messages"][0]["content"]
    assert "reasoning" in prompt


def test_generate_falls_back_to_message(monkeypatch):
    _setup_llm(monkeypatch)
    agent_module = reload_module("agents.answer_generator_agent.agent")

    class DummyAgent:
        def invoke(self, payload):
            return {"output": "", "messages": [{"content": "fallback"}]}

    monkeypatch.setattr(agent_module, "create_agent", lambda **kwargs: DummyAgent())

    agent = agent_module.AnswerGeneratorAgent()
    response = agent.generate("query", "reasoning")

    assert response == "fallback"
