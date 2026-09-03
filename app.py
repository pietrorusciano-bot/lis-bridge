import os
import time

import cloudinary
import requests
from cloudinary import uploader
from flask import Flask, jsonify, render_template, request

import envloader
import store
from lis_translator import LisTranslator

envloader.load_env()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

ASSEMBLYAI_TOKEN_URL = "https://streaming.assemblyai.com/v3/token"

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)


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


def _current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):]
    try:
        r = store.client().auth.get_user(token)
        return r.user.id
    except Exception:
        return None


@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email e password richieste"}), 400
    try:
        r = store.client().auth.sign_up({"email": email, "password": password})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "access_token": r.session.access_token if r.session else None,
        "user_id": r.user.id if r.user else None,
        "user": r.user.email if r.user else email,
    })


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email e password richieste"}), 400
    try:
        r = store.client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    return jsonify({
        "access_token": r.session.access_token,
        "user_id": r.user.id,
        "user": r.user.email,
    })


@app.route("/api/auth/me")
def me():
    user_id = _current_user()
    if not user_id:
        return jsonify({"error": "Non autenticato"}), 401
    return jsonify({"user_id": user_id})


@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    user_id = _current_user()
    return jsonify({"segni": store.get_signs(user_id)})


@app.route("/api/dictionary", methods=["POST"])
def upsert_dictionary():
    user_id = _current_user()
    if not user_id:
        return jsonify({"error": "Non autenticato"}), 401
    data = request.get_json(silent=True) or {}
    try:
        segni = store.upsert_sign(
            user_id,
            data.get("gloss", ""),
            data.get("fsw", ""),
            data.get("validato", False),
            data.get("nota", ""),
            data.get("video", ""),
            personal=True,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"segni": segni})


ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mov"}


@app.route("/api/upload_video", methods=["POST"])
def upload_video():
    user_id = _current_user()
    if not user_id:
        return jsonify({"error": "Non autenticato"}), 401
    gloss = request.form.get("gloss", "").strip().upper()
    file = request.files.get("video")
    if not gloss or not file:
        return jsonify({"error": "glossa o file mancante"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXT:
        return jsonify({"error": "Formato non supportato (usa mp4, webm o mov)"}), 400

    result = uploader.upload(
        file,
        resource_type="video",
        public_id=f"lis_{gloss}_{user_id}",
        overwrite=True,
        folder="lis_bridge",
    )
    video_url = result.get("secure_url", "")

    store.upsert_sign(user_id, gloss, "", False, "", video_url, personal=True)
    return jsonify({"video_url": video_url, "segni": store.get_signs(user_id)})


@app.route("/api/dictionary/<gloss>", methods=["DELETE"])
def delete_dictionary(gloss):
    user_id = _current_user()
    if not user_id:
        return jsonify({"error": "Non autenticato"}), 401
    segni = store.delete_sign(user_id, gloss, personal=True)
    return jsonify({"segni": segni})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
