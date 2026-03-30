import logging

from conftest import clear_logger, reload_module


def test_get_logger_uses_env_name(monkeypatch):
    monkeypatch.setenv("LOGGER_NAME", "env-logger")
    reload_module("config.constants")
    logger_module = reload_module("config.logger")

    clear_logger("env-logger")
    logger = logger_module.get_logger()

    assert logger.name == "env-logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1

    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.formatter is not None
    assert "%(filename)s" in handler.formatter._fmt
    assert "%(funcName)s" in handler.formatter._fmt


def test_get_logger_no_duplicate_handlers(monkeypatch):
    monkeypatch.setenv("LOGGER_NAME", "dup-logger")
    reload_module("config.constants")
    logger_module = reload_module("config.logger")

    clear_logger("dup-logger")
    logger_first = logger_module.get_logger()
    logger_second = logger_module.get_logger()

    assert logger_first is logger_second
    assert len(logger_first.handlers) == 1
