import re, copy



def validate_game_system_create(db, data: dict) -> bool:
    if False in [data.get("codename", False), data.get("name", False), data.get("image-name", False)]:
        return False
    
    if db.structs.find_one({"codename": data.get("codename"), "meta-type": "collection"}):
        return False
    
    if not db.images.find_one({"name": data.get("image_name")}):
        return False
    
    if not re.fullmatch("[0-9a-z\-_]+", data.get("codename")) or len(data.get("codename")) > 45:
        return False
    
    if len(data["name"]) > 45:
        return False
    
    return True


def validate_game_system_change(db, data: dict, sender: dict) -> bool:
    if not data.get("codename", False):
        return False, None
    
    existed_game_system = db.structs.find_one({"codename": data.get("codename"), "type": "game-system"})
    
    if not existed_game_system:
        return False, None

    if existed_game_system.get("owner", "") != sender["username"] and (sender["role"] != "admin" or sender["role"] != "server-admin"): 
        return False, None
    
    return True, existed_game_system
    

def delete_game_system(db, codename: str, sender: dict) -> bool:
    game_system = db.structs.find_one({"codename": codename, "type": "game-system"})

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
        "type": "game-system",
        "meta-type": "collection",
        "owner": sender_user["username"],
        "redactors": reference.get("redactors", [])
        }
    game_system["hash"] = f'{game_system["name"]} {game_system["codename"]} {game_system["image-name"]}'
    return game_system


def update_game_system(instance: dict, reference: dict) -> dict:
    new_instance = copy.deepcopy(instance)
    new_instance["name"] = reference.get("name", None) or instance.get("name")
    new_instance["image-name"] = reference.get("image-name", None) or instance.get("image-name")
    new_instance["redactors"] = reference.get("redactors", None) or instance.get("redactors")
    new_instance["hash"] = f'{instance["name"]} {instance["codename"]} {instance["image-name"]}'
    return new_instance