import os

import cloudinary
import requests
from cloudinary import uploader
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

import envloader
import json_store
from lis_translator import LisTranslator

envloader.load_env()

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

ASSEMBLYAI_TOKEN_URL = "https://streaming.assemblyai.com/v3/token"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/.well-known/assetlinks.json")
def assetlinks():
    path = os.path.join(os.path.dirname(__file__), ".well-known", "assetlinks.json")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="application/json")


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


@app.route("/api/storage_status")
def storage_status():
    return jsonify({
        "github": json_store.github_enabled(),
        "repo": json_store.repo_name(),
        "branch": json_store.branch_name(),
    })


@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    return jsonify({"segni": json_store.get_signs()})


@app.route("/api/dictionary", methods=["POST"])
def upsert_dictionary():
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    data = request.get_json(silent=True) or {}
    try:
        segni = json_store.upsert(
            data.get("gloss", ""),
            fsw=data.get("fsw"),
            nota=data.get("nota"),
            video=data.get("video"),
            image=data.get("image"),
            clear_video=bool(data.get("clear_video")),
            clear_image=bool(data.get("clear_image")),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"segni": segni})


ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mov"}
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@app.route("/api/upload_video", methods=["POST"])
def upload_video():
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    gloss = request.form.get("gloss", "").strip().upper()
    file = request.files.get("video")
    if not gloss or not file:
        return jsonify({"error": "glossa o file mancante"}), 400

    if request.form.get("create_only") in ("1", "true", "yes") and gloss in json_store.get_signs():
        return jsonify({"error": "Parola già presente nel dizionario: " + gloss}), 409

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXT:
        return jsonify({"error": "Formato non supportato (usa mp4, webm o mov)"}), 400

    result = uploader.upload(
        file,
        resource_type="video",
        public_id=f"lis_global_{gloss}",
        overwrite=True,
        folder="lis_bridge",
    )
    video_url = result.get("secure_url", "")

    json_store.upsert(gloss, video=video_url)
    return jsonify({"video_url": video_url, "segni": json_store.get_signs()})


@app.route("/api/upload_image", methods=["POST"])
def upload_image():
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    gloss = request.form.get("gloss", "").strip().upper()
    file = request.files.get("image")
    if not gloss or not file:
        return jsonify({"error": "glossa o file mancante"}), 400

    if request.form.get("create_only") in ("1", "true", "yes") and gloss in json_store.get_signs():
        return jsonify({"error": "Parola già presente nel dizionario: " + gloss}), 409

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return jsonify({"error": "Formato non supportato (usa png, jpg, gif, webp)"}), 400

    result = uploader.upload(
        file,
        resource_type="image",
        public_id=f"lis_global_img_{gloss}",
        overwrite=True,
        folder="lis_bridge",
    )
    image_url = result.get("secure_url", "")

    json_store.upsert(gloss, image=image_url)
    return jsonify({"image_url": image_url, "segni": json_store.get_signs()})


@app.route("/api/dictionary/<gloss>", methods=["DELETE"])
def delete_dictionary(gloss):
    if not _check_admin():
        return jsonify({"error": "Non autorizzato"}), 401
    segni = json_store.delete(gloss)
    return jsonify({"segni": segni})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
