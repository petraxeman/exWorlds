import copy, hashlib
from library import utils
from typing import Union



def process_pack_upload(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("codename"):
        return {"msg": "Undefined pack."}, 401
    
    if data.get("type", "") and (not data.get("type") in ("game-system", "addon", "resource", "adventure", "world", "game")):
        return {"msg": "Wrong type."}, 401
    
    if data.get("reference", {}) and not utils.validate_path(data.get("reference", {})):
        return {"msg": "Wrong path."}, 401
    
    if db.packs.find_one({"codename": data["codename"]}):
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
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, sender)
    db.packs.insert_one(new_pack)

    return {"hash": new_pack["hash"]}, 200


def pack_change(db, data: dict, sender: dict) -> Union[dict, int]:
    pack = db.packs.find_one({"codename": data.get("codename"), "type": "game-system"})

    if "server-admin" not in sender["rights"] and pack["owner"] != sender["username"]:
        return {"msg": "You can't do that."}, 401
    
    updated_pack = update_pack(pack, data)
    db.packs.update_one(pack, {"$set": updated_pack})

    return {"hash": updated_pack["hash"]}, 200


def process_pack_get(db, data: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])

    if not path_list:
        return {"msg": "Undefined path list."}, 401
    
    packs = []
    for path in path_list:
        if not utils.validate_path(path):
            continue
        
        pack = utils.get_by_path(db, path)
        
        if pack:
            del pack["_id"]
            packs.append(pack)

    if not packs:
        return {"msg": "Undefined packs", "p": packs}, 401
    
    return {"packs": packs}, 200


def process_pack_get_hash(db, data: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])
    
    if not path_list:
        return {"msg": "Undefined path list."}, 401
    
    hashes = []
    for path in path_list:
        if not utils.validate_path(path):
            continue
        pack = utils.get_by_path(db, path)

        if pack:
            del pack["_id"]
            hashes.append(pack.get("hash"))
        
    if not hashes:
        return {"msg": "Undefined packs"}, 401
    
    return {"hashes": hashes}, 200


def process_pack_get_by_page(db, data: dict) -> Union[dict, int]:
    if not data.get("type", False):
        return {"msg": "Type undefined"}, 401
    
    pack_type = data.get("type")
    page = int(data.get("page", 1))
    if page < 1:
        return {"msg": "Wrong page range"}, 401
    
    packs = db.packs.find({"type": pack_type}).skip(10 * (page - 1)).limit(10)
    codenames = [el["codename"] for el in packs]
    
    if not codenames:
        return {"msg": "Undefined packs"}
    
    return {"codenames": codenames}, 200


def process_pack_delete(db, data: dict, sender: dict) -> Union[dict, int]:
    codename = data.get("codename", "")
    pack_type = data.get("type", "")
    if not data.get("codename", False) or not pack_type:
        return {"msg": "Undefined codename"}, 401

    pack = db.packs.find_one({"codename": codename, "type": pack_type})
    if not pack:
        return {"msg": "Selected pack not found."}, 401
    
    existed_rights = {"delete-pack", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["username"] != pack["owner"] and (not existed_rights):
        return {"msg": "You can't do that."}, 401
    
    try:
        assert delete_pack(db, pack)
    except Exception:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    return {"msg": f"System {codename} deleted."}, 200


def delete_pack(db, pack: dict) -> bool:
    db.images.delete_one({"name": pack["image-name"]})
    db.packs.delete_one(pack)
    return True


def build_pack(data: dict, sender_user: dict) -> dict:
    game_system = {
        "name": data.get("name"),
        "codename": data.get("codename"),
        "image-name": data.get("image-name"),
        "type": data.get("type"),
        "reference": data.get("reference", {}),
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