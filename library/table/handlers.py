from library import utils
from typing import Union



def process_table_creation(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("reference", "") or not data.get("codename", ""):
        return {"msg": "Undefined path"}, 401
    
    if table := db.tables.find_one({"reference": data.get("reference"), "type": "table", "codename": data.get("codename", "")}):
        return update_table(db, data, sender, table)
    else:
        return create_table(db, data, sender)


def update_table(db, data: dict, sender: dict, original_table: dict) -> Union[dict, int]:
    pack = utils.get_by_path(db, original_table["reference"])

    if not pack:
        return {"msg": "Reference pack does not exists."}, 401
    
    if "server-admin" not in sender["rights"] and sender["username"] not in [pack["owner"], *pack["redactors"]]:
        return {"msg": "You can't do that."}, 401
    
    new_table = build_table(data, sender)
    db.tables.update_one(original_table, {"$set": new_table})
    
    return {"hash": new_table["hash"]}, 200


def create_table(db, data: dict, sender: dict) -> Union[dict, int]:
    existed_rights = {"create-table", "any-create", "server-admin"}.intersection(sender["rights"])
    if not existed_rights:
        return {"msg": "You can't do that."}, 401

    table = build_table(data, sender)
    db.tables.insert_one(table)

    return {"hash": table["hash"]}, 200


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


def build_table(new: dict, origin: dict) -> dict:
    table = {
        "name": new.get("name") or origin.get("name"),
        "codename": origin.get("codename") or new.get("codename"),
        "owner": creator["username"],
        "common": {
            "search-fields": reference.get("search-fields", []),
            "short-view": reference.get("short-view", ["name"]),
            "table-icon": reference.get("table-icon", "opened-book"),
            "table-display": reference.get("search-display", "list"),
        },
        "data": {
            "properties": reference.get("properties", {}),
            "macros": reference.get("macros", {}),
            "schema": reference.get("schema", {}),
            "table-fields": reference.get("table-fields", {})
        }
    }
    table["hash"] = utils.get_hash(str(table))
    table["path"]
    return table