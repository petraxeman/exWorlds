from library import utils
from typing import Union



def process_table_creation(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("reference", "") or not data.get("codename", ""):
        return {"msg": "Undefined path"}, 401
    
    path = utils.path_forward(data["reference"], data["codename"])
    origin_table = utils.get_by_path(path) or {}
    pack = utils.get_by_path(data["reference"])
    new_table = build_table(data, origin_table)

    if not pack:
        return {"msg": "Reference undefined."}, 401
    
    sender_can_redact = sender["username"] in [pack["owner"], *pack["redactors"]]
    if origin_table:
        if "server-admin" not in sender["rights"] and not sender_can_redact:
            return {"msg": "You can't do that."}, 401
        db.tables.update_one(origin_table, new_table)
    else:
        existed_rights = {"create-table", "any-create", "server-admin"}.intersection(sender["rights"])
        if not existed_rights or not sender_can_redact:
            return {"msg": "You can't do that."}, 401
        if not new_table.get("path"):
            new_table["path"] = path
        
        db.tables.insert_one(new_table)
    
    return {"hash": new_table["hash"], "path": new_table["path"]}


def process_table_get(db, data: dict) -> Union[dict, int]:
    if 0 >= len(data.get("path-list", [])) > 10:
        return {"msg": "Tables count is wrong."}, 401

    tables = []
    for path in data["path-list"]:
        if not utils.validate_path(path):
            continue
        
        table = utils.get_by_path(db, path)
        
        if table:
            del table["_id"]
            tables.append(table)

    if not tables:
        return {"msg": "Somthing went wrong. Tables not found."}, 401
    
    return {"tables": tables}, 200


def process_get_by_pack(db, data: dict) -> Union[dict, int]:
    if not data.get("path", ""):
        return {"msg": "Pack path undefined"}, 401
    
    pack = db.packs.find_one({"path": data.get("path")})


def process_table_get_hash(db, data: dict) -> Union[dict, int]:
    if 0 > len(data.get("path-list", [])) > 50:
        return {"msg": "Count of path is wrong."}, 401
    
    hashes = []
    for path in data.get("path-list", []):
        if not utils.validate_path(path):
            continue

        table = utils.get_by_path(db, path)
        
        if table:
            hashes.append(table["hash"])
            
    return {"tables": hashes}, 200
    

def proccess_table_deletion(db, data: dict, sender: dict) -> bool:
    if not utils.validate_path(data):
        return {"msg": "Wrong path."}, 401
    
    table = utils.get_by_path(db, data)
    pack_path = utils.path_up(data)
    pack = utils.get_by_path(db, pack_path)
    
    if not pack or not table:
        return {"msg": "Table or pack not found."}, 401
    
    existed_rights = {"delete-table", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["username"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that."}, 401

    db.tables.delete_one(table)
    
    return {"msg": "Table deletion complete"}, 200


def build_table(new: dict, origin: dict = {}) -> dict:
    table = {
        "name": new.get("name") or origin.get("name"),
        "codename": origin.get("codename") or new.get("codename"),
        "owner": origin.get("owner"),
        "reference": origin.get("path") or new.get("reference"),
        "path": origin.get("path"),
        "common": {
            "search-fields": new.get("search-fields", []) or origin.get("search-fields"),
            "short-view": new.get("short-view") or origin.get("short-view", ["name"]),
            "table-icon": new.get("table-icon") or origin.get("table-icon", "opened-book"),
            "table-display": new.get("search-display") or origin.get("search-display", "list"),
        },
        "data": {
            "properties": new.get("properties") or origin.get("properties", {}),
            "macros": new.get("macros") or origin.get("macros", {}),
            "schema": new.get("schema") or origin.get("schema", []),
            "fields": new.get("fields") or origin.get("fields", {})
        }
    }
    table["hash"] = utils.get_hash(str(table))
    
    return table