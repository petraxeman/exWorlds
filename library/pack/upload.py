import hashlib
from library.search_utils import make_ngram
from library import utils
from typing import Union

"""
Default pack upload request looks like:
{
    "name": "Human readeable name",
    "path": "path://to/pack",
    "imaga-name": "Name of image what be showed as poster",
    "hidden": True,
    "freezed": True,
    "likes": 0,
    "last-update": 01.01.2001,
    "owner": "User who create this pack",
    "redactors": []
}
"""


def process(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("path") or not data.get("image-name"):
        return {"msg": "Undefined pack or undefined poster."}, 401
    
    spath = data.get("path")
    dpath = utils.spath_to_dpath(data.get("path"))
    
    if dpath["exp"] not in ("game-system", "addon", "resource", "adventure", "world", "game"):
        return {"msg": "Wrong type."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (spath,))

    if pack:
        return update_existed(db, data, pack, spath, sender)
    else:
        return upload_new(db, data, spath, sender)


def update_existed(db, data, pack, spath, sender):
    if "server-admin" not in sender["rights"] and pack["owner"] != sender["uid"]:
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, pack)
    db.execute("UPDATE packs SET name = %s, image_name = %s, hash = %s WHERE path = %s",
                (new_pack["name"], new_pack["image-name"], new_pack["hash"], spath))
    return {"hash": new_pack["hash"]}, 200


def upload_new(db, data, spath, sender):
    existed_rights = {"create-pack", "any-create", "server-admin"}.intersection(sender["rights"])
    if not existed_rights:
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, {})
    db.execute("INSERT INTO packs (name, image_name, path, owner, hash) VALUES (%s, %s, %s, %s, %s)",
                (new_pack["name"], new_pack["image-name"], spath, sender["uid"], new_pack["hash"]))
    
    return {"hash": new_pack["hash"]}, 200


def build_pack(new: dict, origin: dict = {}) -> dict:
    pack = {
        "name": new.get("name") or origin.get("name"),
        "image-name": new.get("image-name") or origin.get("image-name"),
        "path": origin.get("path"),
        "readctors": new.get("redactors") or origin.get("redactors"),
    }
    pack["search-field"] = make_ngram(pack["name"], 3, 4)
    pack["hash"] = get_pack_hash(pack)
    
    return pack


def get_pack_hash(instance: dict) -> str:
    return hashlib.md5(
        f'{instance["name"]} {instance["image-name"]}'.encode()).hexdigest()