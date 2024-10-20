from library import utils
from typing import Union



def process_table_creation(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("reference", "") or not data.get("codename", "") or not data.get("reference-type"):
        return {"msg": "Undefined path"}, 401
    if table := db.tables.find_one({"reference": data.get("reference"), "type": "table", "codename": data.get("codename", "")}):
        return update_table(db, data, sender, table)
    else:
        return create_table(db, data, sender)


def update_table(db, data: dict, sender: dict, original_table: dict) -> Union[dict, int]:
    pack = db.packs.find_one({"codename": data["reference"], "type": data["reference-type"]})
    if not pack:
        return {"msg": "Reference pack does not exists."}, 401
    
    if "server-admin" not in sender["rights"] and \
        sender["username"] not in [pack["owner"], *pack["redactors"]]:
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
    if 0 > len(data.get("tables", [])) > 10:
        return {"msg": "Tables count is wrong."}, 401

    tables = []
    for el in data["tables"]:
        if not el.get("codename", "") or not el.get("reference", "") or not el.get("reference-type", ""):
            continue
        
        table = db.tables.find_one({
        "type": "table",
        "codename": el["codename"],
        "reference": el["reference"],
        "reference-type": el["reference-type"]
        })
        
        if table:
            del table["_id"]
            tables.append(table)

    if not tables:
        return {"msg": "Somthing went wrong. Tables not found."}, 401
    
    return {"tables": tables}, 200


def process_table_get_hash(db, data: dict) -> Union[dict, int]:
    if 0 > len(data.get("tables", [])) > 50:
        return {"msg": "Count of tables is wrong."}, 401
    tables = []
    for el in data.get("tables"):
        if not el.get("codename", "") or not el.get("reference", "") or not el.get("reference-type", ""):
            continue
        
        table = db.tables.find_one({"codename": el.get("codename"), "reference": el.get("reference"), "reference-type": el.get("reference-type")})
        
        if table:
            tables.append(table["hash"])
            
    return {"tables": tables}, 200
    

def proccess_table_deletion(db, data: dict, sender: dict) -> bool:
    if not data.get("codename", "") or not data.get("reference", "") or not data.get("reference-type", ""):
        return {"msg": "Required data is not found."}, 401
    
    pack = db.packs.find_one({"codename": data.get("reference"), "type": data.get("reference-type")})
    
    if not pack:
        return {"msg": "Reference pack not found."}, 401
    
    table = db.tables.find_one({"codename": data.get("codename"), "reference": data.get("reference"), "reference-type": data.get("reference-type")})

    if not table:
        return {"msg": "Table not found."}, 401
    
    existed_rights = {"delete-table", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["username"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that."}, 401

    db.tables.delete_one(table)
    
    return {"msg": "Table deletion complete"}, 200


def build_table(reference: dict, creator: dict) -> dict:
    table = {
        "name": reference.get("name"),
        "codename": reference.get("codename"),
        "owner": creator["username"],
        "type": "table",
        "reference": reference.get("reference"),
        "reference-type": reference.get("reference-type"),
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
    return table