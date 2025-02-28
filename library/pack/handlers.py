from typing import Union
from library import utils, contpath


def process_pack_get(db, data: dict, sender: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])

    if 0 > len(path_list) > 30:
        return {"msg": "Undefined path list."}, 401
    
    packs = []
    
    for path in path_list:
        path = contpath.ContentPath.safety(path)
        if not path:
            continue
        
        pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
        
        if pack:
            if pack.get("hidden", False):
                if not utils.verify_access(
                    sender["uid"], sender["rights"],
                    {"server-admin"}, (pack["owner"], *pack["redactors"])):
                    
                    continue
            
            packs.append(pack)

    if not packs:
        return {"msg": "Undefined packs"}, 401
    
    return {"packs": packs}, 200


def process_pack_get_hash(db, data: dict, sender: dict) -> Union[dict, int]:
    path_list = data.get("path-list", [])

    if 0 > len(path_list) > 50:
        return {"msg": "Undefined path list."}, 401
    
    hashes = []

    for path in path_list:
        path = contpath.ContentPath.safety(path)
        if not path:
            continue
        
        pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
        
        if pack:
            if pack.get("hidden", False):
                if not utils.verify_access(
                    sender["uid"], sender["rights"],
                    {"server-admin"}, (pack["owner"], *pack["redactors"])):
                    
                    continue
            
            hashes.append(pack.get("hash"))
        
    if not hashes:
        return {"msg": "Undefined packs"}, 401
    
    return {"hashes": hashes}, 200


def toggle(db, data: dict, sender: dict, arg: str) -> Union[dict, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not pack:
        return {"msg": "Wrong path."}, 401
    
    if not utils.verify_access(
        sender["uid"], sender["rights"],
        {"server-admin"}, (pack["owner"],)):
    
        return {"msg": "You can't do that."}, 401
    
    db.execute(f"UPDATE packs SET {arg} = %s WHERE path = %s", (not pack[arg], pack["path"]))
    
    return {"msg": "Toggle succefull"}, 200


def toggle_list(db, data: dict, sender: dict, arg: str) -> Union[dict, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401

    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not utils.verify_access(
        sender["uid"], sender["rights"],
        {"server-admin"}, (pack["owner"],)):
    
        return {"msg": "You can't do that."}, 401
    
    if path.to_pack in sender["lists"][arg]:
        sender["lists"][arg].pop(path.to_pack)
        pack[arg] -= 1
    else:
        sender["lists"][arg].append(path.to_pack)
        pack[arg] += 1

    db.execute("UPDATE users SET lists = %s WHERE uid = %s", (sender["lists"], sender['uid']))
    db.execute("UPDATE packs SET " + arg + " = %s WHERE path = %s", (pack[arg], pack["path"]))
    return {"msg": "Done"}, 200