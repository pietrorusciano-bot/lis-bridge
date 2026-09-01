import json
import os
import threading

PATH = os.path.join(os.path.dirname(__file__), "static", "dizionario_lis.json")
_lock = threading.Lock()


def load():
    with _lock:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    return data.get("segni", {})


def save(segni):
    with _lock:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump({"segni": segni}, f, ensure_ascii=False, indent=2)


def upsert(gloss, fsw, validato=False, nota="", video=""):
    gloss = gloss.strip().upper()
    if not gloss:
        raise ValueError("La glossa non può essere vuota")
    segni = load()
    existing = segni.get(gloss, {})
    segni[gloss] = {
        "fsw": (fsw or "").strip(),
        "validato": bool(validato),
        "nota": (nota or "").strip(),
        "video": (video or existing.get("video", "")).strip(),
    }
    save(segni)
    return segni


def delete(gloss):
    gloss = gloss.strip().upper()
    segni = load()
    segni.pop(gloss, None)
    save(segni)
    return segni
