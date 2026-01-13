import json
from pathlib import Path

WAIT_SECS = 1  # how many seconds we wait between retries
RETRIES = 30  # sometimes fetch requests for the various links fails. this controls how many retries
TOKENS = 300  # how many tokens we take from each article, to be later fed as input to the LLM
MAX_ARTICLES = 15  # maximum amount of filtered articles we feed into the LLM (say each day in production)

DEFAULT_TONE = 3  # 1 neutral, 2 general, 3 heated, 4 humoristic

_SETTINGS_PATH = Path("data") / "settings.json"

def get_tone():
    try:
        if _SETTINGS_PATH.exists():
            data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
            tone = int(data.get("tone", DEFAULT_TONE))
            if tone in (1, 2, 3, 4):
                return tone
    except Exception:
        pass
    return DEFAULT_TONE


def set_tone(tone: int) -> None:
    tone = int(tone)
    if tone not in (1, 2, 3, 4):
        raise ValueError("tone must be 1, 2, 3, or 4")

    _SETTINGS_PATH.parent.mkdir(exist_ok=True)
    _SETTINGS_PATH.write_text(json.dumps({"tone": tone}, indent=2), encoding="utf-8")