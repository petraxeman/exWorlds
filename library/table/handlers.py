from library import utils



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
        # Inheritance
        "owner": creator["username"],
        "collection": reference.get("collection"),
        "game-system": reference.get("game-system"),
        "type": "table",
        # Table information
        "name": reference.get("name"),
        "codename": reference.get("codename"),
        "search-fields": reference.get("search-fields", []),
        "short-view": reference.get("short-view", ["name"]),
        "table-icon": reference.get("table-icon", "opened-book"),
        "table-display": reference.get("search-display", "list"),
        "properties": reference.get("properties", {}),
        "macros": reference.get("macros", {}),
        "schema": reference.get("schema", {}),
        "table-fields": reference.get("table-fields", {})
    }
    table["hash"] = utils.get_hash(str(table))
    return table


# FixMe: REWRITE THIS CODE! THIS CODE IS TEMP BECOUSE NOTE FORMAT UNDEFINED 27.08.2024
def delete_table_and_notes(db, table_codename: str, collection: str):
    notes = db.structs.find({"type": "note", "table": table_codename, "collection": collection})
    for note in notes:
        del note
    
    db.structs.delete_one({"collection": collection, "codename": table_codename,"type": "table"})