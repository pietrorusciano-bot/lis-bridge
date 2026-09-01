import os
import time
import uuid

import requests
from flask import Flask, jsonify, render_template, request, send_from_directory

import dictionary
from glossary import Glossary
from lis_translator import LisTranslator

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

glossary = Glossary()

ASSEMBLYAI_TOKEN_URL = "https://streaming.assemblyai.com/v3/token"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "static", "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)


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
            data.get("video", ""),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"segni": segni})


ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mov"}


@app.route("/api/upload_video", methods=["POST"])
def upload_video():
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    gloss = request.form.get("gloss", "").strip().upper()
    file = request.files.get("video")
    if not gloss or not file:
        return jsonify({"error": "glossa o file mancante"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXT:
        return jsonify({"error": "Formato non supportato (usa mp4, webm o mov)"}), 400

    filename = f"{gloss}{ext}"
    path = os.path.join(VIDEO_DIR, filename)
    file.save(path)

    video_url = f"/static/videos/{filename}"
    dictionary.upsert(gloss, "", False, "", video_url)
    return jsonify({"video_url": video_url, "segni": dictionary.load()})


@app.route("/api/dictionary/<gloss>", methods=["DELETE"])
def delete_dictionary(gloss):
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    segni = dictionary.delete(gloss)
    return jsonify({"segni": segni})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
