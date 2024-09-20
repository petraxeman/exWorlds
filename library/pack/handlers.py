import re, copy, hashlib
from typing import Union


def process_pack_upload(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("codename"):
        return {"msg": "Undefined pack"}, 401

    if pack := db.packs.find_one({"codename": data["codename"]}):
        print(pack)
        return pack_change(db, data, sender)
    else:
        return pack_create(db, data, sender)


def pack_create(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("name", None) or not data.get("image-name", None):
        return {"msg": "Undefined pack"}, 401
    
    if not db.images.find_one({"name": data["image-name"]}):
        return {"msg": "Image does not exists"}, 401

    existed_rights = {"create-pack", "any-create", "server-admin"}.intersection(sender["rights"])
    if not existed_rights:
        print("create", sender['rights'], existed_rights)
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, sender)
    db.packs.insert_one(new_pack)

    return {"hash": new_pack["hash"]}


def pack_change(db, data: dict, sender: dict) -> Union[dict, int]:
    pack = db.packs.find_one({"codename": data.get("codename"), "type": "game-system"})

    existed_rights = {"server-admin", "change-pack", "any-change"}.intersection(sender["rights"])
    if not existed_rights and pack["owner"] != sender["username"]:
        print("change", sender['rights'], existed_rights)
        return {"msg": "You can't do that."}, 401
    
    updated_pack = update_pack(pack, data)
    db.packs.update_one(pack, {"$set": updated_pack})

    return {"hash": updated_pack["hash"]}, 200


def delete_game_system(db, codename: str, sender: dict) -> bool:
    game_system = db.packs.find_one({"codename": codename, "type": "game-system"})

    if not game_system:
        return False
    
    if game_system["owner"] != sender["username"] and (sender["role"] not in ["admin", "server-admin"]):
        return False

    db.images.delete_one({"name": game_system["image-name"]})
    db.packs.delete_one(game_system)
    db.packs.delete_many({"type": "table", "game-system": codename})

    notes = db.packs.find({"type": "note", "game-system": codename})
    for note in notes:
        for field in note.get("note", []):
            if field.get("type", "") == "image":
                db.images.delete_one({"name": field.get("value", "")})
    db.structs.delete_many({"type": "note", "game-system": codename})
    return True


def build_pack(data: dict, sender_user: dict) -> dict:
    game_system = {
        "name": data.get("name"),
        "codename": data.get("codename"),
        "image-name": data.get("image-name"),
        "type": data.get("type"),
        "reference": data.get("reference"),
        "hash": get_pack_hash(data),
        "owner": sender_user["username"],
        "redactors": data.get("redactors", [])
        }
    return game_system


def update_pack(instance: dict, reference: dict) -> dict:
    new_instance = copy.deepcopy(instance)
    new_instance["name"] = reference.get("name", None) or instance.get("name")
    new_instance["image-name"] = reference.get("image-name", None) or instance.get("image-name")
    new_instance["redactors"] = reference.get("redactors", None) or instance.get("redactors")
    new_instance["hash"] = get_pack_hash(new_instance)
    return new_instance


def get_pack_hash(instance: dict) -> str:
    return hashlib.md5(
        f"{instance["name"]} {instance["codename"]} {instance["image-name"]}".encode()
        ).hexdigest()