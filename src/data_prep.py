from pathlib import Path
from datetime import datetime

from logger import get_logger

logger = get_logger(__name__)


def prune_old_jsonl_files(data_dir: Path, keep: int = 10):
    jsonl_files = sorted(
        data_dir.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for old_file in jsonl_files[keep:]:
        try:
            old_file.unlink()
        except Exception as e:
            logger.warning("Failed to delete old jsonl file %s: %s",old_file,e)


def create_run_output_file(keep_last: int = 10):
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = data_dir / f"{timestamp}.jsonl"

    # create file immediately so it counts as newest
    output_path.touch(exist_ok=True)

    prune_old_jsonl_files(data_dir, keep=keep_last)

    return output_path
