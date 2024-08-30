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



@bp.route("/game-system/upload", methods = ["POST"])
@token_required
def game_system_upload():
    db = current_app.config["MONGODB_INST"]
    
    result = handlers.validate_game_system_upload(db, request.json, request.current_user)

    if not result[0]:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    system = None
    if result[1] == "create":
        system = handlers.build_game_system(request.json, request.current_user)
        db.structs.insert_one(system)
    elif result[1] == "change":
        instance = db.structs.find_one({"codename": request.json["codename"], "type": "game-system"})
        system = handlers.update_game_system(instance, request.json)
        db.structs.update_one(instance, {"$set": system})
    else:
        return {"msg": "Somthing went wrong. Try again later."}, 401

    
    return {"hash": system["hash"]}, 200


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
    page = int(request.json.get("page", 1))
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