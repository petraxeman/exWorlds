from library import utils


def validate_table_creation_request(db, request: dict, game_system: dict, sender: dict) -> bool:
    expected_properties = ["name",
                           "codename",
                           "search-fields",
                           "short-view",
                           "schema",
                           "table-fields"]
    request_keys = list(request.keys())
    for exp_prop in expected_properties:
        if exp_prop not in request_keys:
            return False
    
    if not game_system:
        return False
    
    if sender["username"] != game_system["owner"] and sender["username"] not in game_system["redactors"]:
        return False
    
    if db.structs.find_one({
        "type": "table",
        "name": request.json.get("name"),
        "codename": request.json.get("codename"),
        "game-system": request.json.get("game-system")}):
        return False
    return True


def build_table(reference: dict, creator: dict) -> dict:
    table = {
        # Information about Inheritance
        "owner": creator["username"],
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
    table["hash"] = utils.get_hash("table")
    return table