from library import utils, contpath
from typing import Union


def by_pack(db, data: dict, sender: dict) -> Union[dict, int]:
    path = contpath.ContentPath.safety(data.get("path", ""), "gc:", "pack")
    if not path:
        return {"msg": "Wrong path."}, 401

    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not pack:
        return {"msg": "Pack not found"}, 401
    
    if pack["hidden"] and not utils.verify_access(sender["uid"], sender["rights"], {"server-admin"}, (pack["owner"], *pack["redactors"],)):
        return {"msg": "Pack not found"}, 401
    
    tables = db.fetchall("SELECT * FROM tables WHERE starts_with(path, %s)", (path.to_pack,))

    match data.get("mode", "pathes"):
        case "full":
            return {"tables": tables}
        case "hashes":
            return {"hashes": [table["hash"] for table in tables]}
        case "pathes":
            return {"pathes": [table["path"] for table in tables]}
    
    return {"msg": "Somthing went wrong"}, 401


def specific(db, data: dict, sender: dict) -> Union[dict, int]:
    pathes_count = len(data.get("path-list", []))
    if 0 >= pathes_count or pathes_count > 10:
        return {"msg": "Tables count is wrong."}, 401

    tables = grab_tables(db, sender, data["path-list"], "full")
    
    if not tables:
        return {"msg": "No one table you send not found."}, 401
    
    return {"tables": tables}, 200


def hash(db, data: dict, sender: dict) -> Union[dict, int]:
    pathes_count = len(data.get("path-list", []))
    if 0 >= pathes_count or pathes_count > 50:
        return {"msg": "Count of path is wrong."}, 401
    
    hashes = grab_tables(db, sender, data["path-list"], "hash")
    
    if not hashes:
        return {"msg": "No one table you send not found."}, 401
            
    return {"hashes": hashes}, 200


def grab_tables(db, sender: dict, path_list: list, get: str = "hash") -> list:
    data = []
    access = {
        "allowed": [],
        "not-allowed": []
    }
    
    for path in path_list:
        path = contpath.ContentPath.safety(path, "gc:", "table")
        if not path:
            continue
        
        if path.to_pack in access["not-allowed"]:
            continue
        elif path.to_pack not in access["allowed"]:
            pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
            if pack["hidden"]:    
                if not utils.verify_access(sender["uid"], sender["rights"], {"server-admin"}, [pack["owner"], *pack["redactors"]]):
                    access["not-allowed"].append(path.to_pack)
                    continue
                access["allowed"].append(path.to_pack)
            
        table = db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_table,))
        
        match get:
            case "hash":
                data.append(table["hash"])
            case "full":
                data.append(table)
    
    return data