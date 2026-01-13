import logging
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

_LOGGERS = {}


def get_file_logger(name: str, filename: str, level=logging.INFO, fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"):
    key = (name, filename)
    if key in _LOGGERS:
        return _LOGGERS[key]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    log_path = DATA_DIR / filename

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)

    _LOGGERS[key] = logger
    return logger


# ---- default app logger (backward compatible) ----
def get_logger(name: str):
    return get_file_logger(
        name=name,
        filename="log.txt",
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
