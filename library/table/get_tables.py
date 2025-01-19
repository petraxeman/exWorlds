from library import utils
from typing import Union


def by_pack(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("path", None):
        return {"msg": "Pack path not found"}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (data["path"],))
    
    if not pack:
        return {"msg": "Pack not found"}, 401
    
    if pack["hidden"]:    
        if (pack["owner"] != sender["uid"]) and ("server-admin" not in sender["rights"]) and (sender["uid"] not in pack["redactors"]):
            return {"msg": "Pack not found"}, 401
    
    table_path = "table://" + data["path"].split("://")[1]
    tables = db.fetchall("SELECT * FROM tables WHERE  starts_with(path, %s)", (table_path,))

    match data.get("mode", "pathes"):
        case "full":
            return {"tables": tables}
        case "hashes":
            return {"hashes": [table["hash"] for table in tables]}
        case "pathes":
            return {"pathes": [table["path"] for table in tables]}
    
    return {"msg": "Somthing went wrong"}, 401


def specific(db, data: dict, sender: dict) -> Union[dict, int]:
    if 0 >= len(data.get("path-list", [])) > 10:
        return {"msg": "Tables count is wrong."}, 401

    tables = []
    for path in data["path-list"]:
        table = get_specific_table(db, path, sender)
        
        if table:
            tables.append(table)

    if not tables:
        return {"msg": "Somthing went wrong. Tables not found."}, 401
    
    return {"tables": tables}, 200


def hash(db, data: dict, sender: dict) -> Union[dict, int]:
    if 0 > len(data.get("path-list", [])) > 50:
        return {"msg": "Count of path is wrong."}, 401
    
    hashes = []
    for path in data.get("path-list", []):
        table = get_specific_table(db, path, sender)
        
        if table:
            hashes.append(table["hash"])
            
    return {"hashes": hashes}, 200


def get_specific_table(db, spath: str, sender: dict) -> dict:
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (utils.table_to_pack(spath),))
    table = db.fetchone("SELECT * FROM tables WHERE path = %s", (spath,))
    
    if not table:
        return {}
    
    if pack["hidden"]:    
        if (pack["owner"] != sender["uid"]) and ("server-admin" not in sender["rights"]) and (sender["uid"] not in pack["redactors"]):
            return {}
    
    return table
    