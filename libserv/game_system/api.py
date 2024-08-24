import hashlib
import re
from libserv.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-auth", __name__)



@bp.route("/game-system/create", methods = ["POST"])
@token_required
def create_system():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    data = request.json
    
    if False in [data.get("codename", False), data.get("name", False), data.get("image_name", False)]:
        return {"msg": "Lost some data"}
    
    if not db.images.find_one({"name": data["image_name"]}):
        return {"msg": "Image does not exist"}, 401
    
    if not re.fullmatch("[0-9a-z\-_]+", data["codename"]) or len(data["codename"]) > 45:
        return {"msg": "Wrong codename"}, 401
    
    if game_system := db.structs.find_one({"author": current_user["username"], "codename": data["codename"], "type": "game-system"}):
        return {"msg": f"You already use this codename for <{game_system["name"]}>"}, 401
    
    new_system = {
        "name": data["name"],
        "codename": data["codename"],
        "image_name": data["image_name"],
        "type": "game-system",
        "author": current_user["username"]
        }
    
    hash = hashlib.md5(str(new_system).encode()).hexdigest()
    new_system["hash"] = hash
    db.structs.insert_one(new_system)
    return {"hash": hash}, 200


@bp.route("/game-system/get", methods = ["POST"])
@token_required
def get_system():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    codename = request.json.get("codename", "")
    
    if not codename:
        return {"msg": "Undefined system"}, 401
    
    system = db.structs.find_one({"author": current_user["username"], "type": "game-system", "codename": codename})
    
    if not system:
        return {"msg": "Undefined system"}, 401
    
    del system["type"]
    del system["_id"]

    return system, 200


@bp.route("/game-system/get-hash", methods = ["POST"])
@token_required
def get_system_hash():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    codename = request.json.get("codename", "")
    
    if not codename:
        return {"msg": "Undefined system"}, 401
    
    game_system = db.structs.find_one({"author": current_user["username"], "type": "game-system", "codename": codename})
    if not game_system:
        return {"msg": "Undefined system"}, 401
    
    return {"hash": game_system["hash"]}, 200


@bp.route("/game-system/get-by-page", methods = ["POST"])
@token_required
def get_systems():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    data = request.json
    page = data.get("page", 1)
    
    systems = db.structs.find({"type": "game-system"}).skip(10 * (page - 1)).limit(10)
    codenames = [el["codename"] for el in systems]
    
    return {"systems": codenames}, 200


@bp.route("/game-systems/get-count", methods = ["POST"])
@token_required
def get_systems_count():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    
    count = db.structs.count_documents({"type": "game-system"})
    
    return {"count": count}


@bp.route("/game-systems/delete", methods = ["POST"])
@token_required
def delete_system():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    
    if not request.json.get("codename", False):
        return {"msg": "Undefined codename"}, 401
    
    game_system = db.structs.find_one({"author": current_user["username"], "codename": request.json["codename"], "type": "game-system"})
    db.images.delete_one({"name": game_system["image_name"]})
    db.structs.delete_one(game_system)
    
    tables = db.structs.find({"type": "table", "author": current_user["username"], "game-system": game_system["codename"]})
    for table in tables:
        notes = db.structs.find({"type": "note", "author": current_user["username"], "game-system": game_system["codename"]})
        for note in notes:
            for field in note:
                if field.get("type", "Undefined") == "image":
                    db.images.delete_one({"name": field.get("value", "")})
        db.structs.delete_many({"type": "note", "author": current_user["username"], "game-system": game_system["codename"], "table": table["codename"]})
    db.structs.delete_many({"type": "table", "author": current_user["username"], "game-system": game_system["codename"]})
    
    return {"Ok": True}, 200