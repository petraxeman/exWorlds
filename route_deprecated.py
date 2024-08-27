from server import app, db
from flask import request, send_file, Response
from werkzeug.utils import secure_filename
import uuid, io, jwt, datetime, re, json, hashlib, copy, numexpr, math
from functools import wraps



def token_required(fn):  
    @wraps(fn)  
    def decorator(*args, **kwargs):
        global current_user
        token = request.headers.get("Auth-Token", None)
        if not token:  
            return {"msg": "Valid token is missing"}
        try:
            data = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
            if datetime.datetime.strptime(data["expire_date"], "%d-%m-%Y") < datetime.datetime.utcnow():
                return {"msg": "Token expired"}, 403
            current_user = db.users.find_one({"username": data["username"]})
            if not current_user:
                return {"msg": "Undefined token"}, 403
            return fn(*args, **kwargs)
        except Exception as err:
            print(err)
            return {"msg": "Wrong token"}, 403
    return decorator 



# ===================== #
# === MACROS ROUTES === #
# ===================== #

@app.route("/macro/upload", methods = ["POST"])
@token_required
def upload_macros():
    return {}, 200


@app.route("/macro/get", methods = ["POST"])
@token_required
def get_macros():
    pass


# ==================== #
# === TABLE ROUTES === #
# ==================== #





def build_string_from_list(arr: list) -> str:
    _ = ""
    for el in arr:
        _ += str(el) + " "
    return _.strip()

def dice_to_statistic(text: str) -> dict:
    dice_match = re.findall("((?:[1-9][0-9]*)?d\d+|d\d+|\d+|\(|\)|\+|\-|\*|\/)", str(text))
    min_array = []
    max_array = []
    if dice_match != "":
        for element in dice_match:
            if re.findall("((?:[1-9][0-9]*)?d\d+)", str(element)) != []:
                dice_levels = element.split("d", )
                min_array.append(int(dice_levels[0]))
                max_array.append(int(dice_levels[0]) * int(dice_levels[1]))
            elif re.findall("(\d+)", str(element)) != []:
                min_array.append(int(element))
                max_array.append(int(element))
            else:
                min_array.append(element)
                max_array.append(element)
    min_value = int(numexpr.evaluate(build_string_from_list(min_array)).item())
    max_value = int(numexpr.evaluate(build_string_from_list(max_array)).item())
    avg_value = (max_value + min_value) // 2
    return {"min": min_value, "max": max_value, "avg": avg_value, "org": text, "type": "number"}

def is_dice(text: str) -> bool:
    if re.findall("([1-9][0-9]?d\d+|d\d+|\d+|\+|\-|\*|\/)", str(text)):
        return True
    return False

def format_note(note_data: dict):
    new_note_data = copy.deepcopy(note_data)
    for codename in note_data:
        if note_data[codename]["type"] == "number":
            if isinstance(note_data[codename], int) or isinstance(note_data[codename], float):
                new_note_data[codename] = {"min": note_data[codename], "max": note_data[codename], "avg": note_data[codename], "org": note_data[codename], "type": "number"}
            elif is_dice(note_data[codename]["value"]):
                new_note_data[codename] = dice_to_statistic(note_data[codename]["value"])
    return new_note_data

@app.route("/gameSystem/table/createNote", methods = ["POST"])
@token_required
def create_note():
    if not request.headers.get("Game-System", False) or not request.headers.get("Table-Codename", False):
        return {"msg": "Bad request"}, 401
    
    if db.structs.count_documents({"author": current_user["username"], "type": "game_system", "codename": request.headers.get("Game-System", False)}) == 0:
        return {"msg": "Game system not found"}, 401
    
    if db.structs.count_documents({
        "author": current_user["username"],
        "type": "schema",
        "game_system": request.headers.get("Game-System", ""),
        "codename": request.headers.get("Table-Codename", "")}
        ) == 0:
        return {"msg": "Table not found"}, 401
    
    note_filter = {
        "author": current_user["username"],
        "type": "note",
        "game_system": request.headers.get("Game-System", ""),
        "table_codename": request.headers.get("Table-Codename", ""),
        "codename": request.json["codename"]["value"]
        }
    
    note_hash = ""
    if db.structs.count_documents(note_filter) != 0:
        data = copy.copy(request.json)
        data["codename"]["value"] = db.structs.find_one(note_filter)["codename"]
        note_hash = hashlib.md5(str(data).encode()).hexdigest()
        db.structs.update_one(note_filter, {
            "$set": {
                "hash": note_hash,
                "note": format_note(data)
            }
        })
    else:
        note_hash = hashlib.md5(str(request.json).encode()).hexdigest()
        note: dict = {
            "author": current_user["username"],
            "type": "note",
            "game_system": request.headers.get("Game-System", ""),
            "table_codename": request.headers.get("Table-Codename", ""),
            "codename": request.json["codename"]["value"],
            "note": format_note(request.json),
            "hash": note_hash,
        }
        db.structs.insert_one(note)
    
    return {"Ok": True, "hash": note_hash}


@app.route("/gameSystem/table/getNote", methods = ["POST"])
@token_required
def get_note():
    if not request.headers.get("Game-System", False) or not request.headers.get("Table-Codename", False) or not request.headers.get("Note-Codename", False):
        return {"msg": "Bad request"}, 401

    finded_note = db.structs.find_one({
        "author": current_user["username"],
        "game_system": request.headers["Game-System"],
        "table_codename": request.headers["Table-Codename"],
        "codename": request.headers["Note-Codename"],
        "type": "note"})
    
    if not finded_note:
        return {"msg": "Wrong data, note does not exists"}, 401
    
    return {"note": finded_note["note"], "hash": finded_note["hash"]}, 200


@app.route("/gameSystem/table/getNoteHash", methods = ["POST"])
@token_required
def get_note_hash():
    if not request.headers.get("Game-System", False) or not request.headers.get("Table-Codename", False) or not request.headers.get("Note-Codename", False):
        return {"msg": "Bad request"}, 401

    finded_note = db.structs.find_one({
        "author": current_user["username"],
        "game_system": request.headers["Game-System"],
        "table_codename": request.headers["Table-Codename"],
        "codename": request.headers["Note-Codename"],
        "type": "note"})
    
    
    if not finded_note:
        return {"msg": "Wrong data, note does not exists"}, 401
    
    return {"hash": finded_note["hash"]}, 200


def search_by_user_filter(base_filter: dict, user_filter: dict, page: int, count: bool = False):
    filters = []
    table = db.structs.find_one({"game_system": base_filter["game_system"], "codename": base_filter["table_codename"], "type": "schema"})
    
    if user_filter["text"] != "":
        indexes = []
        for field in table["table_fields"]:
            if table["table_fields"][field]["type"] in ["string", "paragraph"]:
                indexes.append((f"note.{field}.value", "text"))
        db.structs.create_index(indexes)
        filters.append({"$match": {"$text": {"$search": user_filter["text"]}}})
    filters.append({"$match": base_filter})

    for field in user_filter["fields"]:
        field_type = table["table_fields"].get(field, {}).get("type", "undefined")
        match field_type:
            case "undefined":
                continue
            case x if x in ["string", "paragraph"]:
                filters.append({
                    "$match": { f"note.{field}.value": {"$regex": conver_text_to_regex(user_filter["fields"][field].get("value", ""))}}
                })
            case "number":
                postfix = "avg"
                if user_filter["fields"][field].get("cehck_min_value", False):
                    postfix = "min"
                elif user_filter["fields"][field].get("cehck_max_value", False):
                    postfix = "max"
                filters.append({
                        "$match": { f"note.{field}.{postfix}": {"$gte": user_filter["fields"][field].get("min", 0), "$lte": user_filter["fields"][field].get("max", 1000)}}
                    })
            case "bool":
                filters.append({
                    "$match": { f"note.{field}.value": {"$eq": user_filter["fields"][field].get("value", False)}}
                })
            case "list":
                filters.append({
                    "$match": {
                               f"note.{field}.value": {"$regex": conver_text_to_regex(user_filter["fields"][field].get("value", ""))}
                            }
                        })
    if count:
        filters.append({"$count": "notes"})
        result = db.structs.aggregate(filters)
        db.structs.drop_indexes()
        return result
    if page > 1:
        filters.append({"$skip": (page - 1) * 15})
    filters.append({"$limit": 15})
    print(filters)
    result = db.structs.aggregate(filters)
    db.structs.drop_indexes()
    return result

def conver_text_to_regex(text: str):
    tokens = text.split(" ")
    regex = "(?i)"
    for token in tokens:
        regex += f"(?=.*{token})"
    return regex


@app.route("/gameSystem/table/getNotes", methods = ["POST"])
@token_required
def get_notes():
    if not request.headers.get("Game-System", False) or not request.headers.get("Table-Codename", False):
        return {"msg": "Bad request"}, 401
    
    page = int(request.headers.get("Page", 1))
    base_filter = {"game_system": request.headers["Game-System"], "table_codename": request.headers["Table-Codename"], "type": "note"}
    user_filter = {"text": request.json["text"], "fields": request.json["fields"]}
    
    if request.headers.get("Note-Count", False):
        for result in search_by_user_filter(base_filter, user_filter, page, True):
            return {"count": math.ceil(result["notes"] / 15)}
        return {"count": 0}
    response = []
    result = search_by_user_filter(base_filter, user_filter, page)
    for row in result:
        response.append(row["codename"])
    return {"notes": response}


@app.route("/tabletop/game-system/table/delete-note", methods = ["POST"])
@token_required
def delete_note():
    if not request.headers.get("Game-System", False) or not request.headers.get("Table-Codename", False) or not request.headers.get("Note-Codename", False):
        return {"msg": "Bad request"}, 401
    
    filter = {"type": "note", "game_system": request.headers.get("Game-System"), "table_codename": request.headers.get("Table-Codename"), "codename": request.headers.get("Note-Codename")}
    note = db.structs.find_one(filter)
    for field in note["note"]:
        try:
            if field.get("type", "undefined") == "image":
                db.images.delete_one({"name": field.get("value")})
        except:
            pass
    db.structs.delete_one(filter)
    return {}, 200