import hashlib
from library.search_utils import make_ngram
from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("codename"):
        return {"msg": "Undefined pack."}, 401
    
    if data.get("type", "") and (not data.get("type") in ("game-system", "addon", "resource", "adventure", "world", "game")):
        return {"msg": "Wrong type."}, 401
    
    pack = db.packs.find_one({"path": data["codename"]}) or {}
    new_pack = build_pack(data, pack)
    
    if pack:
        if "server-admin" not in sender["rights"] and pack["owner"] != sender["username"]:
            return {"msg": "You can't do that."}, 401
        db.packs.update_one(pack, {"$set": new_pack})
    else:
        existed_rights = {"create-pack", "any-create", "server-admin"}.intersection(sender["rights"])
        if not existed_rights:
            return {"msg": "You can't do that."}, 401
        new_pack["owner"] = sender["username"]
        db.packs.insert_one(new_pack)
        return {"hash": new_pack["hash"]}, 200


def build_pack(new: dict, origin: dict = {}) -> dict:
    pack = {
        "name": new.get("name") or origin.get("name"),
        "codename": origin.get("codename") or new.get("codename"),
        "image-name": new.get("image-name") or origin.get("image-name"),
        "type": origin.get("type") or new.get("type"),
        "reference": origin.get("reference") or new.get("reference"),
        "path": origin.get("path"),
        "hidden": False,
        "freezed": False,
        "likes": 0,
        "last-update": 0,
        "owner": origin.get("owner") or new.get("owner"),
        "readctors": new.get("redactors") or origin.get("redactors"),
    }
    pack["search-field"] = make_ngram(pack["name"], 3, 4)
    pack["hash"] = get_pack_hash(pack)
    if not pack["path"]:
        points = []
        if pack["reference"]:
            points.append(pack["reference"])
        points.append(pack["codename"])
        pack["path"] = "pack://" + "/".join(points) 
    return pack


def get_pack_hash(instance: dict) -> str:
    return hashlib.md5(
        f"{instance["name"]} {instance["codename"]} {instance["image-name"]}".encode()
        ).hexdigest()