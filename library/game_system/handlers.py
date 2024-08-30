import re, copy, hashlib



def validate_game_system_upload(db, data: dict, sender: dict) -> bool:
    if not data.get("codename", False):
        return False, None
    
    action = "nothing"
    if db.structs.find_one({"codename": data.get("codename"), "type": "game-system"}):
        action = "change"
        if not validate_game_system_change(db, data, sender):
            return False, None
    else:
        action = "create"
        if not validate_game_system_create(db, data):
            return False, None
    
    return True, action
    

def validate_game_system_create(db, data: dict) -> bool:
    if not data.get("name", None) or not data.get("image-name", None):
        return False
    
    if db.structs.find_one({"codename": data["codename"], "is-collection": True}):
        return False
    
    if not db.images.find_one({"name": data.get("image-name")}):
        return False

    return True


def validate_game_system_change(db, data: dict, sender: dict) -> bool:
    game_system = db.structs.find_one({"codename": data.get("codename"), "type": "game-system"})

    if game_system.get("owner", "") != sender["username"] and (sender["role"] != "admin" and sender["role"] != "server-admin"): 
        return False
    
    return True
    

def delete_game_system(db, codename: str, sender: dict) -> bool:
    game_system = db.structs.find_one({"codename": codename, "type": "game-system"})

    if not game_system:
        return False
    
    if game_system["owner"] != sender["username"] and (sender["role"] not in ["admin", "server-admin"]):
        return False

    db.images.delete_one({"name": game_system["image-name"]})
    db.structs.delete_one(game_system)
    db.structs.delete_many({"type": "table", "game-system": codename})

    notes = db.structs.find({"type": "note", "game-system": codename})
    for note in notes:
        for field in note.get("note", []):
            if field.get("type", "") == "image":
                db.images.delete_one({"name": field.get("value", "")})
    db.structs.delete_many({"type": "note", "game-system": codename})
    return True


def build_game_system(reference: dict, sender_user: dict) -> dict:
    game_system = {
        "name": reference.get("name"),
        "codename": reference.get("codename"),
        "image-name": reference.get("image-name"),
        "is-collection": True,
        "type": "game-system",
        "owner": sender_user["username"],
        "redactors": reference.get("redactors", [])
        }
    game_system["hash"] = hashlib.md5(f'{game_system["name"]} {game_system["codename"]} {game_system["image-name"]}'.encode()).hexdigest()
    return game_system


def update_game_system(instance: dict, reference: dict) -> dict:
    new_instance = copy.deepcopy(instance)
    new_instance["name"] = reference.get("name", None) or instance.get("name")
    new_instance["image-name"] = reference.get("image-name", None) or instance.get("image-name")
    new_instance["redactors"] = reference.get("redactors", None) or instance.get("redactors")
    new_instance["hash"] = hashlib.md5(f'{new_instance["name"]} {new_instance["codename"]} {new_instance["image-name"]}'.encode()).hexdigest()
    return new_instance