from flask import Flask, render_template, request, redirect
import json
import os
from typing import Dict

from logger import get_file_logger
from config import get_tone, set_tone

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "../templates"))
app.secret_key = os.getenv("SECRET_KEY")

MSG_PATH = "messages.json"

TONE_LABELS:dict[int,str] = {
    1: "neutral",
    2: "general opinion",
    3: "heated opinion",
    4: "humoristic opinion",
}

user_logger = get_file_logger(
    name="user_actions",
    filename="user_log.txt",
    fmt="%(asctime)s | %(message)s"
)

def log_user_action(action: str, **fields)->None:
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "-")
    extras = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
    user_logger.info("%s | ip=%s | ua=%s | %s", action, ip, ua, extras)

def load_messages()->Dict[str, str]:
    with open(MSG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_messages(messages: Dict[str, str]) -> None:
    with open(MSG_PATH, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

@app.route("/")
def index():
    messages = load_messages()
    return render_template(
        "handler_page.html",
        messages=messages,
        current_tone=get_tone(),
        tone_labels=TONE_LABELS
    )

@app.route("/toggle", methods=["POST"])
def toggle():
    messages = load_messages()
    entity = request.form["entity"]
    if entity in messages:
        before = messages[entity]
        messages[entity] = "False" if messages[entity] == "True" else "True"
        after = messages[entity]
        save_messages(messages)
        log_user_action("toggle", entity=entity, before=before, after=after)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    messages = load_messages()
    entity = request.form["entity"]
    if entity in messages:
        before = messages[entity]
        del messages[entity]
        save_messages(messages)
        log_user_action("delete", entity=entity, before=before)
    return redirect("/")

@app.route("/add", methods=["POST"])
def add():
    messages = load_messages()
    entity = request.form["entity"].strip()
    bias = request.form["bias"].strip()

    if entity and bias in ("True", "False"):
        existed = entity in messages
        previous = messages.get(entity)
        messages[entity] = bias
        save_messages(messages)
        log_user_action("add", entity=entity, bias=bias, existed=existed, previous=previous)

    return redirect("/")

@app.route("/tone", methods=["POST"])
def tone():
    tone_raw = request.form.get("tone", "").strip()
    before = get_tone()

    try:
        set_tone(int(tone_raw))
        after = get_tone()
        log_user_action("tone_change", before=before, after=after)
    except Exception:
        log_user_action("tone_change_invalid", attempted=tone_raw, current=before)

    return redirect("/")
    

if __name__ == "__main__":
    app.run(debug=True)
