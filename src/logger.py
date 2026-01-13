import logging
from pathlib import Path

LOG_DIR = Path("data")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "log.txt"

logging.getLogger().handlers.clear()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)

def get_logger(name: str):
    return logging.getLogger(name)
