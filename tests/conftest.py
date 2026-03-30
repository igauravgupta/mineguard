import importlib
import logging
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def reload_module(module_name: str):
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


def clear_logger(name: str):
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.handlers.clear()
    logger.propagate = False


def reset_llm_singleton():
    try:
        import providers.llm as llm_module
    except Exception:
        return

    llm_module.LLMProvider._instance = None
    llm_module.LLMProvider._initialized = False


class DummyResponse:
    def __init__(self, content: str):
        self.content = content


class DummyChatLiteLLM:
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    def invoke(self, prompt: str):
        return DummyResponse(f"echo: {prompt}")
