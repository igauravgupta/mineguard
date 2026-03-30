from conftest import reload_module


def test_constants_with_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key123")
    monkeypatch.setenv("LLM_MODEL_NAME", "model-x")
    monkeypatch.setenv("LOGGER_NAME", "test-logger")

    constants = reload_module("config.constants")

    assert constants.Constants.GROQ_API_KEY == "key123"
    assert constants.Constants.LLM_MODEL_NAME == "model-x"
    assert constants.Constants.LOGGER_NAME == "test-logger"


def test_constants_defaults(monkeypatch):
    # Set empty strings so .env values do not override during import.
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("LLM_MODEL_NAME", "")
    monkeypatch.setenv("LOGGER_NAME", "")

    constants = reload_module("config.constants")

    assert constants.Constants.GROQ_API_KEY == ""
    assert constants.Constants.LLM_MODEL_NAME == ""
    assert constants.Constants.LOGGER_NAME == ""
