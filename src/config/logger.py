import logging

from config.constants import Constants


def get_logger(name: str | None = None) -> logging.Logger:
	"""Return a configured app logger that logs to the console."""
	logger_name = name or Constants.LOGGER_NAME
	logger = logging.getLogger(logger_name)
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)

	handler = logging.StreamHandler()
	# TODO: Switch to JSON structured logs with fields like level, module, line,
	# request_id, trace_id, and user_id for production observability.
	formatter = logging.Formatter(
		"[%(asctime)s]:(%(filename)s):(%(funcName)s):%(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.propagate = False

	return logger
