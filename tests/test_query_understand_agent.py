from conftest import DummyChatLiteLLM, reload_module, reset_llm_singleton


def _setup_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")
    monkeypatch.setattr(llm_module, "ChatLiteLLM", DummyChatLiteLLM)
    reset_llm_singleton()


def test_detect_intent_from_output(monkeypatch):
    _setup_llm(monkeypatch)

    agent_module = reload_module("agents.quey_understand_agent.agent")

    class DummyAgent:
        def invoke(self, payload):
            return {"output": "legal query"}

    monkeypatch.setattr(
        agent_module,
        "create_agent",
        lambda model, tools, system_prompt: DummyAgent(),
    )

    agent = agent_module.QueryUnderstandAgent()
    assert agent.detect_intent("what is the law?") == "legal query"


def test_detect_intent_from_messages(monkeypatch):
    _setup_llm(monkeypatch)

    agent_module = reload_module("agents.quey_understand_agent.agent")

    class DummyAgent:
        def invoke(self, payload):
            return {"output": "", "messages": [{"content": "incident reporting"}]}

    monkeypatch.setattr(
        agent_module,
        "create_agent",
        lambda model, tools, system_prompt: DummyAgent(),
    )

    agent = agent_module.QueryUnderstandAgent()
    assert agent.detect_intent("we had an accident") == "incident reporting"


def test_detect_intent_unknown_label(monkeypatch):
    _setup_llm(monkeypatch)

    agent_module = reload_module("agents.quey_understand_agent.agent")

    class DummyAgent:
        def invoke(self, payload):
            return {"output": "something else"}

    monkeypatch.setattr(
        agent_module,
        "create_agent",
        lambda model, tools, system_prompt: DummyAgent(),
    )

    agent = agent_module.QueryUnderstandAgent()
    assert agent.detect_intent("random") == "legal query"
