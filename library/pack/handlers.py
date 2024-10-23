import copy, hashlib
from library import utils
from typing import Union



def process_pack_upload(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("codename"):
        return {"msg": "Undefined pack."}, 401
    
    if data.get("type", "") and (not data.get("type") in ("game-system", "addon", "resource", "adventure", "world", "game")):
        return {"msg": "Wrong type."}, 401
    
    pack = db.packs.find_one({"path": data["codename"]}) or {}
    new_pack = build_pack(data, sender, pack)
    
    if pack:
        if "server-admin" not in sender["rights"] and pack["owner"] != sender["username"]:
            return {"msg": "You can't do that."}, 401
        db.packs.update_one(pack, {"$set": new_pack})
    else:
        existed_rights = {"create-pack", "any-create", "server-admin"}.intersection(sender["rights"])
        if not existed_rights:
            return {"msg": "You can't do that."}, 401
        db.packs.insert_one(new_pack)
        return {"hash": new_pack["hash"]}, 200


def process_pack_get(db, data: dict, sender: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])

    if 0 > len(path_list) > 10:
        return {"msg": "Undefined path list."}, 401
    
    existed_rigths = {"server-admin"}.intersection(sender["rights"])
    packs = []
    for path in path_list:
        
        pack = utils.get_by_path(db, path)
        
        if pack:
            if pack.get("hidden", False):
                if sender["username"] not in [pack["owner"], *pack["readactors"]] or not existed_rigths:
                    continue
            
            del pack["_id"]
            packs.append(pack)

    if not packs:
        return {"msg": "Undefined packs", "p": packs}, 401
    
    return {"packs": packs}, 200


def process_pack_get_hash(db, data: dict, sender: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])

    if 0 > len(path_list) > 50:
        return {"msg": "Undefined path list."}, 401
    
    existed_rigths = {"server-admin"}.intersection(sender["rights"])
    hashes = []
    for path in path_list:

        pack = utils.get_by_path(db, path)
        
        if pack:
            if pack.get("hidden", False):
                if sender["username"] not in [pack["owner"], *pack["readactors"]] or not existed_rigths:
                    continue

            del pack["_id"]
            hashes.append(pack.get("hash"))
        
    if not hashes:
        return {"msg": "Undefined packs"}, 401
    
    return {"hashes": hashes}, 200


def process_pack_get_by_page(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("type", ""):
        return {"msg": "Type undefined"}, 401
    
    pack_type = data.get("type")
    page = int(data.get("page", 1))
    if page < 1:
        return {"msg": "Wrong page range"}, 401
    
    pipeline = [
        {"$match": {"$expr": {"$eq": ["$type", pack_type]}}},
        {
            "$addFields": {
                "is-favorite": {
                    "$cond": {
                        "if": {"$in": ["$path", sender["lists"]["favorites"]]},
                        "then": True,
                        "else": False,
                    }
                }
            }
        },        
        {
            "$match": {
                "$or": [
                    {"hidden": False},
                    {"$or": [
                        {"owner": sender["username"]}, 
                        {"redactors": {"$in": [sender["username"]]}}
                        ]
                    }
                ]
            }
        },
        {
            "$sort": {
                "text-score": -1,
                "is-favorite": -1,
                "likes": -1
            }
        },
        {"$limit": 10},
    ]

    if 10 * (page - 1) != 0:
        pipeline.append({"$skip": 10 * (page - 1)})

    packs = db.packs.aggregate(pipeline)
    
    codenames = []
    for el in packs:
        del el["_id"]
        codenames.append(el["codename"])

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


def toggle(db, data: dict, sender: dict, arg: str):
    pack = utils.get_by_path(db, data.get("path", ""))

    if sender["username"] != pack["owner"] and "server-admin" not in sender["rights"]:
        return {"msg": "You can't do that."}, 401
    
    if pack.get(arg, False):
        db.packs.update_one(pack, {"$set": {arg: False}})
    else:
        db.packs.update_one(pack, {"$set": {arg: True}})
    
    return {"msg": "Toggle succefull"}, 200


def toggle_list(db, data: dict, sender: dict, arg: str):
    if not data.get("path", ""):
        return {"msg": "Path not found"}, 401
    
    if data in sender["lists"][arg]:
        db.users.update_one(sender, {"$pull": {"lists." + arg: data.get("path")}})
    else:
        db.users.update_one(sender, {"$push": {"lists." + arg: data.get("path")}})
    return {"msg": "Done"}, 200


def build_pack(new: dict, sender: dict, origin: dict = {}) -> dict:
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