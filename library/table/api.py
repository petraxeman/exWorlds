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



@bp.route("/game-system/get-table", methods = ["POST"])
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


def get_fields(table: list) -> dict:
    fields: dict = {}
    for row in table:
        new_fields: dict = parse_row(row, 0)
        for codename in new_fields.keys():
            if codename in fields.keys():
                continue
            fields[codename] = new_fields[codename]
    return fields

def parse_row(data: list, rlvl: int = 0):
    if rlvl >= 15:
        return []
    
    fields: dict = {}
    for element in data:
        if element["type"] == "block":
            for row in element["rows"]:
                new_fields: dict = parse_row(row, rlvl + 1)
                for codename in new_fields.keys():
                    if codename in fields.keys():
                        continue
                    fields[codename] = new_fields[codename]
        if element["type"] == "tabs_container":
            for tab in element["tabs"]:
                for row in tab["rows"]:
                    new_fields: dict = parse_row(row, rlvl + 1)
                    for codename in new_fields.keys():
                        if codename in fields.keys():
                            continue
                        fields[codename] = new_fields[codename]
        else:
            codename = element.get("codename", "")
            if codename:
                match element.get("type", "undefined"):
                    case "string":
                        if element.get("as_type", "") != "":
                            fields[codename] = {"type": "string", "name": element.get("name", ""), "as_type": [substr.strip() for substr in element.get("as_type").split(";")]}
                        else:
                            fields[codename] = {"type": "string", "name": element.get("name", "")}
                    case "number":
                        fields[codename] = {"type": "number", "name": element.get("name", ""), "subtype": element.get("subtype", "integer")}
                    case field_type:
                        fields[codename] = {"type": field_type, "name": element.get("name", "")}
                #fields[codename] = {"type": element.get("type", "string")}
    return fields


@bp.route("/gameSystem/createTable", methods = ["POST"])
@token_required
def create_table():
    db = current_app.config["MNOGODB_INST"]
    game_system = db.structs.find_one({"type": "game-system", "codename": request.json.get("game-system", "")})

    result = handlers.validate_table_creation_request(db, request.json, game_system, request.current_user)
    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401

    table = handlers.build_table(request.json, request.current_user)
    db.structs.insert_one(table)

    return {"hash": table["hash"]}, 200


@bp.route("/gameSystem/deleteTable", methods = ["POST"])
@token_required
def delete_table():
    if not request.json.get("game_system", False) or not request.json.get("table_name", False):
        return {"msg": "\"Game system\" or \"Table name\" is undefined"}, 401
    db.structs.delete_one({"author": current_user["username"], "type": "schema", "codename": request.json["table_name"], "game_system": request.json["game_system"]})
    return {}, 200