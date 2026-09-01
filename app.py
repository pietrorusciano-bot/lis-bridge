import os
import time

import requests
from flask import Flask, jsonify, render_template, request

import dictionary
from glossary import Glossary
from lis_translator import LisTranslator

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

glossary = Glossary()

ASSEMBLYAI_TOKEN_URL = "https://streaming.assemblyai.com/v3/token"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


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


def _check_admin():
    if not ADMIN_PASSWORD:
        return True
    token = request.headers.get("X-Admin-Token", "")
    return token == ADMIN_PASSWORD


@app.route("/api/admin_status")
def admin_status():
    return jsonify({"auth_required": bool(ADMIN_PASSWORD)})


@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    return jsonify({"segni": dictionary.load()})


@app.route("/api/dictionary", methods=["POST"])
def upsert_dictionary():
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    data = request.get_json(silent=True) or {}
    try:
        segni = dictionary.upsert(
            data.get("gloss", ""),
            data.get("fsw", ""),
            data.get("validato", False),
            data.get("nota", ""),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"segni": segni})


@app.route("/api/dictionary/<gloss>", methods=["DELETE"])
def delete_dictionary(gloss):
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    segni = dictionary.delete(gloss)
    return jsonify({"segni": segni})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
