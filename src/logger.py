import logging
from pathlib import Path
from typing import Dict, Tuple

DATA_DIR:Path = Path("data")
DATA_DIR.mkdir(exist_ok=True)

_LOGGERS: Dict[Tuple[str, str], logging.Logger] = {}


def get_file_logger(name: str, filename: str, level=logging.INFO, fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"):
    key:tuple[str,str] = (name, filename)
    if key in _LOGGERS:
        return _LOGGERS[key]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    log_path:Path = DATA_DIR / filename

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)

    _LOGGERS[key] = logger
    return logger


# default app logger
def get_logger(name: str):
    return get_file_logger(name=name, filename="log.txt", fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
