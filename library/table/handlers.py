from library import utils
from typing import Union



def process_table_upload(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("path"):
        return {"msg": "Undefind operation"}, 401
    
    parent_pack_path = utils.table_to_pack(data["path"])
    parent_pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (parent_pack_path,))
    
    if not parent_pack:
        return {"msg": "Wrong path"}, 401
    
    if sender["uid"] not in [parent_pack["owner"], *parent_pack["redactors"]] and "server-admin" not in sender["rights"]:
        return {"msg": "You can't do that"}, 401
    
    data["owner"] = sender["uid"]
    if origin := db.fetchone("SELECT * FROM tables WHERE path = %s", (data["path"],)):
        table = build_table(data, origin)
        db.execute("UPDATE tables SET name = %(name)s, common = %(common)s, data = %(data)s, hash = %(hash)s WHERE path = %(path)s", table)
        return {"msg": "Updating table success", "hash": table["hash"]}
    else:
        table = build_table(data)
        db.execute("INSERT INTO tables (name, path, owner, common, data, hash) VALUES (%(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", table)
        return {"msg": "Creating table success", "hash": table["hash"]}
    return {"msg": "Somthing went wrong"}, 401


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
        "owner": origin.get("owner") or new.get("owner"),
        "path": origin.get("path") or new.get("path"),
        "common": {
            "search-fields": new.get("search-fields", []) or origin.get("search-fields", ["name"]),
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