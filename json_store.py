import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request

import envloader

envloader.load_env()

PATH = os.path.join(os.path.dirname(__file__), "dizionario_globale.json")

REPO = (os.environ.get("GITHUB_REPO", "") or "").strip()
TOKEN = (os.environ.get("GITHUB_TOKEN", "") or "").strip()
BRANCH = (os.environ.get("GITHUB_BRANCH", "") or "main").strip()
FILE_PATH = (os.environ.get("DICT_PATH", "") or "dizionario_globale.json").strip()
COMMITTER_NAME = (os.environ.get("GITHUB_COMMIT_NAME", "") or "LIS Bridge").strip()
COMMITTER_EMAIL = (os.environ.get("GITHUB_COMMIT_EMAIL", "") or "lisbridge@users.noreply.github.com").strip()

_lock = threading.Lock()
_cache = None
_cache_time = 0.0
_CACHE_TTL = 15  # secondi

_API = "https://api.github.com/repos/{repo}/contents/{path}"


def _use_github():
    return bool(REPO and TOKEN)


def _headers():
    return {
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "lis-bridge",
    }


def _gh_read():
    url = _API.format(repo=REPO, path=FILE_PATH) + "?ref=" + BRANCH
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode("utf-8"))
    raw = base64.b64decode(data["content"]).decode("utf-8")
    parsed = json.loads(raw) if raw.strip() else {}
    return parsed.get("segni", {}), data.get("sha")


def _gh_write(segni, message):
    content = json.dumps({"segni": segni}, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    url = _API.format(repo=REPO, path=FILE_PATH)

    last_error = None
    for _ in range(3):
        sha = None
        try:
            _, sha = _gh_read()
        except urllib.error.HTTPError as e:
            if e.code != 404:
                last_error = e
        except Exception as e:
            last_error = e

        body = {
            "message": message,
            "content": encoded,
            "branch": BRANCH,
            "committer": {"name": COMMITTER_NAME, "email": COMMITTER_EMAIL},
        }
        if sha:
            body["sha"] = sha

        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="PUT", headers=_headers()
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                json.loads(r.read().decode("utf-8"))
            return True
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code in (409, 422):
                time.sleep(0.6)
                continue
            raise
        except Exception as e:
            last_error = e
            time.sleep(0.6)
    if last_error:
        raise last_error
    return False


def _local_read():
    if not os.path.exists(PATH):
        return {}
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("segni", {})


def _local_write(segni):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump({"segni": segni}, f, ensure_ascii=False, indent=2)


def load():
    global _cache, _cache_time
    with _lock:
        if _cache is not None and (time.time() - _cache_time) < _CACHE_TTL:
            return _cache
        if _use_github():
            try:
                segni, _ = _gh_read()
                _cache = segni
                _cache_time = time.time()
                _local_write(segni)
                return segni
            except Exception:
                pass
        segni = _local_read()
        _cache = segni
        _cache_time = time.time()
        return segni


def save(segni, message="Aggiorna dizionario globale dei segni"):
    global _cache, _cache_time
    with _lock:
        _cache = segni
        _cache_time = time.time()
        _local_write(segni)
        if _use_github():
            _gh_write(segni, message)


def get_signs():
    return load()


def upsert(gloss, fsw=None, validato=None, nota=None, video=None, image=None,
           clear_video=False, clear_image=False):
    gloss = gloss.strip().upper()
    if not gloss:
        raise ValueError("La glossa non può essere vuota")
    segni = load()
    existing = segni.get(gloss, {})
    if clear_video:
        new_video = ""
    elif video is not None:
        new_video = video.strip()
    else:
        new_video = existing.get("video", "")
    if clear_image:
        new_image = ""
    elif image is not None:
        new_image = image.strip()
    else:
        new_image = existing.get("image", "")
    segni[gloss] = {
        "fsw": existing.get("fsw", "") if fsw is None else fsw.strip(),
        "validato": existing.get("validato", False) if validato is None else bool(validato),
        "nota": existing.get("nota", "") if nota is None else nota.strip(),
        "video": new_video,
        "image": new_image,
    }
    save(segni, message="Aggiorna segno: " + gloss)
    return segni


def delete(gloss):
    gloss = gloss.strip().upper()
    segni = load()
    segni.pop(gloss, None)
    save(segni, message="Elimina segno: " + gloss)
    return segni
