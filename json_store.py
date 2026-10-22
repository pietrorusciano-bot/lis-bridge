import json
import os
import threading

PATH = os.path.join(os.path.dirname(__file__), "dizionario_globale.json")
_lock = threading.Lock()


def load():
    with _lock:
        if not os.path.exists(PATH):
            return {}
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    return data.get("segni", {})


def save(segni):
    with _lock:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump({"segni": segni}, f, ensure_ascii=False, indent=2)


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
    save(segni)
    return segni


def delete(gloss):
    gloss = gloss.strip().upper()
    segni = load()
    segni.pop(gloss, None)
    save(segni)
    return segni
