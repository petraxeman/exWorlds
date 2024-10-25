import copy, hashlib
from library import utils
from typing import Union



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