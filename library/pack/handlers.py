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
        
        pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path,))
        
        if pack:
            if pack.get("hidden", False):
                if sender["username"] not in [pack["owner"], *pack["readactors"]] or not existed_rigths:
                    continue
            
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

        pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path,))
        
        if pack:
            if pack.get("hidden", False):
                if sender["username"] not in [pack["owner"], *pack["readactors"]] or not existed_rigths:
                    continue

            hashes.append(pack.get("hash"))
        
    if not hashes:
        return {"msg": "Undefined packs"}, 401
    
    return {"hashes": hashes}, 200


def toggle(db, data: dict, sender: dict, arg: str):
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (data.get("path", "://"),))

    if not pack:
        return {"msg": "Wrong path."}
    
    if sender["uid"] != pack["owner"] and "server-admin" not in sender["rights"]:
        return {"msg": "You can't do that."}, 401
    
    db.execute(f"UPDATE packs SET {arg} = %s WHERE path = %s", (not pack[arg], pack["path"]))
    
    return {"msg": "Toggle succefull"}, 200


def toggle_list(db, data: dict, sender: dict, arg: str):
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (data.get("path", "://"),))
    
    if not pack:
        return {"msg": "Wrong path."}
    
    if data["path"] in sender["lists"][arg]:
        sender["lists"][arg].pop(data["path"])
    else:
        sender["lists"][arg].append(data["path"])
    
    db.execute("UPDATE users SET lists = %s", (sender["lists"]))
    
    return {"msg": "Done"}, 200