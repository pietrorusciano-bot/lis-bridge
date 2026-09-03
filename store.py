import os

import envloader
from supabase import create_client

envloader.load_env()

_url = os.environ.get("SUPABASE_URL", "")
_service = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

_client = create_client(_url, _service)


def client():
    return _client


def get_signs(user_id):
    result = {}
    r = _client.table("signs").select("*").is_("user_id", "null").execute()
    for row in r.data:
        gloss = (row.get("gloss") or "").strip().upper()
        if gloss:
            result[gloss] = _to_entry(row)
    if user_id:
        r2 = _client.table("signs").select("*").eq("user_id", user_id).execute()
        for row in r2.data:
            gloss = (row.get("gloss") or "").strip().upper()
            if gloss:
                result[gloss] = _to_entry(row)
    return result


def _to_entry(row):
    return {
        "fsw": row.get("fsw") or "",
        "validato": bool(row.get("validato")),
        "nota": row.get("nota") or "",
        "video": row.get("video") or "",
        "user_id": row.get("user_id"),
    }


def upsert_sign(user_id, gloss, fsw="", validato=False, nota="", video="", personal=True):
    gloss = gloss.strip().upper()
    if not gloss:
        raise ValueError("La glossa non può essere vuota")
    owner = user_id if personal else None
    query = _client.table("signs").select("*").eq("gloss", gloss)
    if owner:
        query = query.eq("user_id", owner)
    else:
        query = query.is_("user_id", "null")
    r = query.execute()
    data = {
        "fsw": (fsw or "").strip(),
        "validato": bool(validato),
        "nota": (nota or "").strip(),
        "video": (video or "").strip(),
    }
    if r.data:
        _client.table("signs").update(data).eq("id", r.data[0]["id"]).execute()
    else:
        data["gloss"] = gloss
        data["user_id"] = owner
        _client.table("signs").insert(data).execute()
    return get_signs(user_id)


def delete_sign(user_id, gloss, personal=True):
    gloss = gloss.strip().upper()
    owner = user_id if personal else None
    query = _client.table("signs").delete().eq("gloss", gloss)
    if owner:
        query = query.eq("user_id", owner)
    else:
        query = query.is_("user_id", "null")
    query.execute()
    return get_signs(user_id)
