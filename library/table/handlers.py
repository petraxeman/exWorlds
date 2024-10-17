from library import utils
from typing import Union



def process_table_creation(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("pack-codename", "") or not data.get("codename", ""):
        return {"msg": "Undefined path"}, 401

    if table := db.structs.find_one({"reference": data.get("pack-codename"), "type": "table", "codename": data.get("codename", "")}):
        return update_table(db, data, sender, table)
    else:
        return create_table(db, data, sender)


def update_table(db, data: dict, sender: dict, original_table: dict) -> Union[dict, int]:
    if "server-admin" not in sender["rights"] and not sender["username"] != original_table["owner"]:
        return {"msg": "You can't do that."}, 401
    
    new_table = build_table(data)
    db.tables.update_one(original_table, {"$set": new_table})
    
    return {"hash": new_table["hash"]}, 200


def create_table(db, data: dict, sender: dict) -> Union[dict, int]:
    existed_rights = {"create-table", "any-create", "server-admin"}.intersection(sender["rights"])
    if not existed_rights:
        return {"msg": "You can't do that."}, 401

    table = build_table(data, sender)
    db.structs.insert_one(table)

    return {"hash": table["hash"]}, 200



def validate_table_deletion(db, request: dict, sender: dict) -> bool:
    if not request.get("collection-codename", False) or not request.get("table-codename", False):
        return False
    
    collection = db.structs.find_one({"meta": "collection", "codename": request["collection-codename"]})

    if sender["username"] not in [*collection["redactors"], collection["owner"]] and sender["role"] not in ["admin", "server-admin"]:
        return False
    
    return True


def validate_table_creation_request(db, request: dict, collection: dict, sender: dict) -> bool:
    expected_properties = ["collection",
                           "name",
                           "codename",
                           "search-fields",
                           "short-view",
                           "schema",
                           "table-fields"]
    
    request_keys = list(request.keys())
    for exp_prop in expected_properties:
        if exp_prop not in request_keys:
            return False
    
    if not collection:
        return False
    
    if sender["username"] not in [*collection["redactors"], collection["owner"]] and sender["role"] not in ["admin", "server-admin"]:
        return False
    
    if db.structs.find_one({
        "type": "table",
        "name": request.json.get("name"),
        "codename": request.json.get("codename"),
        "collection": request.json.get("game-system")}):
        return False
    
    return True


def build_table(reference: dict, creator: dict) -> dict:
    table = {
        "name": reference.get("name"),
        "codename": reference.get("codename"),
        "owner": creator["username"],
        "type": "table",
        "reference": reference.get("pack-codename"),
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


def validate_table(reference: dict):
    pass



# FixMe: REWRITE THIS CODE! THIS CODE IS TEMP BECOUSE NOTE FORMAT UNDEFINED 27.08.2024
def delete_table_and_notes(db, table_codename: str, collection: str):
    notes = db.structs.find({"type": "note", "table": table_codename, "collection": collection})
    for note in notes:
        del note
    
    db.structs.delete_one({"collection": collection, "codename": table_codename,"type": "table"})