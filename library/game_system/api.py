import hashlib
import re
from library.game_system import handlers
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-game-systems", __name__)



@bp.route("/game-system/create", methods = ["POST"])
@token_required
def game_system_create():
    db = current_app.config["MONGODB_INST"]
    
    result = handlers.validate_game_system_create(db, request.json, request.current_user["username"])
    
    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    new_system = handlers.build_game_system(request.json, request.current_user)

    db.structs.insert_one(new_system)

    return {"hash": new_system["hash"]}, 200


@bp.route("/game-system/change", methods = ["POST"])
@token_required
def game_system_change():
    db = current_app.config["MONGODB_INST"]

    result, instance = handlers.validate_game_system_change(db, request.json, request.current_user)
    original = db.structs.find_one(instance)

    if original["image-name"] != instance["image-name"]:
        db.images.delete_one({"name": original["image-name"]})

    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    changed_system = handlers.update_game_system(instance, request.json)
    db.structs.update_one(instance, changed_system)
    return {"hash": changed_system["hash"]}, 200


@bp.route("/game-system/get", methods = ["POST"])
@token_required
def get_system():
    db = current_app.config["MONGODB_INST"]
    codename = request.json.get("codename", "")
    
    if not codename:
        return {"msg": "Undefined system"}, 401
    
    existed_game_system = db.structs.find_one({"type": "game-system", "codename": codename})
    
    if not existed_game_system:
        return {"msg": "Undefined system"}, 401
    
    del existed_game_system["type"]
    del existed_game_system["_id"]

    return existed_game_system, 200


@bp.route("/game-system/get-hash", methods = ["POST"])
@token_required
def get_system_hash():
    db = current_app.config["MONGODB_INST"]
    codename = request.json.get("codename", "")
    
    if not codename:
        return {"msg": "Undefined system"}, 401
    
    existed_game_system = db.structs.find_one({"type": "game-system", "codename": codename})
    if not existed_game_system:
        return {"msg": "Undefined system"}, 401
    
    return {"hash": existed_game_system["hash"]}, 200


@bp.route("/game-system/get-systems-by-page", methods = ["POST"])
@token_required
def get_systems():
    db = current_app.config["MONGODB_INST"]
    page = request.json.get("page", 1)
    systems = db.structs.find({"type": "game-system"}).skip(10 * (page - 1)).limit(10)
    codenames = [el["codename"] for el in systems]
    return {"systems": codenames}, 200


@bp.route("/game-systems/get-count", methods = ["POST"])
@token_required
def get_systems_count():
    db = current_app.config["MONGODB_INST"]
    count = db.structs.count_documents({"type": "game-system"})
    return {"count": count}


@bp.route("/game-systems/delete", methods = ["POST"])
@token_required
def delete_system():
    db = current_app.config["MONGODB_INST"]
    
    if not request.json.get("codename", False):
        return {"msg": "Undefined codename"}, 401
    
    result = handlers.delete_game_system(db, request.json.get("codename"), request.current_user)
    
    if not result:
        return {"msg": "Somthing went wrong. Try again later"}, 401
    
    return {"msg": f"System <{request.json.get("codename")}> deleted."}, 200