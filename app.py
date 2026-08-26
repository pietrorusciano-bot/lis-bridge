import os
import time

import requests
from flask import Flask, jsonify, render_template, request

from glossary import Glossary
from lis_translator import LisTranslator

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

glossary = Glossary()

ASSEMBLYAI_TOKEN_URL = "https://streaming.assemblyai.com/v3/token"


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500


@app.route("/api/stream_token")
def stream_token():
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        return jsonify({"error": "ASSEMBLYAI_API_KEY mancante"}), 500
    r = requests.get(
        ASSEMBLYAI_TOKEN_URL,
        headers={"Authorization": key},
        params={"expires_in_seconds": 600},
        timeout=60,
    )
    r.raise_for_status()
    return jsonify(r.json())


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"italiano": "", "lis": ""})

    translator = LisTranslator()
    try:
        result = translator.translate(text)
    except Exception as e:
        result = {"italiano": "", "lis": "", "errore_lis": str(e)}
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
