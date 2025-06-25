from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "../templates"))

MSG_PATH = "messages.json"

def load_messages():
    with open(MSG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_messages(messages):
    with open(MSG_PATH, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

@app.route("/")
def index():
    messages = load_messages()
    return render_template("messages.html", messages=messages)

@app.route("/toggle", methods=["POST"])
def toggle():
    messages = load_messages()
    entity = request.form["entity"]
    if entity in messages:
        messages[entity] = "False" if messages[entity] == "True" else "True"
        save_messages(messages)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    messages = load_messages()
    entity = request.form["entity"]
    if entity in messages:
        del messages[entity]
        save_messages(messages)
    return redirect("/")

@app.route("/add", methods=["POST"])
def add():
    messages = load_messages()
    entity = request.form["entity"]
    bias = request.form["bias"]
    messages[entity] = bias
    save_messages(messages)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
