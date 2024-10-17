import hashlib
import re
from library.table import handlers
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-table", __name__)



@bp.route("/pack/table/upload")
@token_required
def talbe_upload():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_table_creation(db, request.json, request.current_user)


@bp.route("/pack/table/get", methods = ["POST"])
@token_required
def get_table():
    db = current_app.config["MNOGODB_INST"]
    current_user = request.current_user

    if not request.json.get("game-system", False) or not request.json.get("table-name", False):
        return {"msg": '"Game system" or "Table name" is undefined'}, 401
    
    table = db.structs.find_one({
        "owner": current_user["username"],
        "type": "schema",
        "codename": request.json["table_name"],
        "game_system": request.json["game_system"]
        })
    return {"table_data": schema["table_data"], "search_fields": schema["search_fields"], "table_fields": schema["table_fields"], "hash": schema["hash"]}, 200


@bp.route("/gameSystem/getTableHash", methods = ["POST"])
@token_required
def get_table_hash():
    if not request.json.get("game_system", False) or not request.json.get("table_name", False):
        return {"msg": "\"Game system\" or \"Table name\" is undefined"}, 401
    schema = db.structs.find_one({"author": current_user["username"], "type": "schema", "codename": request.json["table_name"], "game_system": request.json["game_system"]})
    return {"hash": schema["hash"]}, 200


@bp.route("/gameSystem/getTables", methods = ["POST"])
@token_required
def get_tables():
    system_codename = request.json.get("system_codename")
    schemas = db.structs.find({"type": "schema", "game_system": system_codename})
    schemas = [{"codename": schema["codename"], "icon": schema["icon"], "name": schema["name"], } for schema in schemas]
    return {"schemas": schemas}, 200





@bp.route("/collection/delete-table", methods = ["POST"])
@token_required
def delete_table():
    db = current_app.config["MNOGODB_INST"]
    
    result = handlers.validate_table_deletion(db, request.json, request.current_user)
    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    handlers.delete_table_and_notes(db, request.json["game-system-codename"], request.json["table-codename"])
    return {"msg": "Table deletion complete"}, 200