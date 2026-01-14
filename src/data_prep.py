from pathlib import Path
from datetime import datetime

from logger import get_logger

logger = get_logger(__name__)


def prune_old_jsonl_files(data_dir: Path, keep: int = 10)->None:
    jsonl_files:list[Path] = sorted(data_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)

    for old_file in jsonl_files[keep:]:  # delete oldest outputs, to keep to a max of 10 outputs in the data dir
        try:
            old_file.unlink()
        except Exception as e:
            logger.warning("Failed to delete old jsonl file %s: %s",old_file,e)


def create_timestamped_output_file(keep_last: int = 10)->Path:
    data_dir:Path = Path("data")
    data_dir.mkdir(exist_ok=True)

    timestamp:str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path:Path = data_dir / f"{timestamp}.jsonl"

    # create file immediately so it counts as newest
    output_path.touch(exist_ok=True)

    prune_old_jsonl_files(data_dir, keep=keep_last)

    return output_path
