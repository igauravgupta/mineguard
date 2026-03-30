import pytest

from conftest import DummyChatLiteLLM, reset_llm_singleton, reload_module


def _reload_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")
    monkeypatch.setattr(llm_module, "ChatLiteLLM", DummyChatLiteLLM)
    reset_llm_singleton()

    return llm_module


def test_llm_provider_singleton(monkeypatch):
    llm_module = _reload_llm(monkeypatch)

    first = llm_module.LLMProvider()
    second = llm_module.LLMProvider()

    assert first is second
    assert first.model_name == "model-x"
    assert first.api_key == "key123"


def test_llm_provider_missing_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")
    reset_llm_singleton()

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        llm_module.LLMProvider()


def test_llm_provider_missing_model_name(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "")
    reload_module("config.constants")

    llm_module = reload_module("providers.llm")
    reset_llm_singleton()

    with pytest.raises(ValueError, match="LLM_MODEL_NAME"):
        llm_module.LLMProvider()


def test_generate_response(monkeypatch):
    llm_module = _reload_llm(monkeypatch)
    provider = llm_module.LLMProvider()

    response = provider.generate_response("hi")

    assert response == "echo: hi"
