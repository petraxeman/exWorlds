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



# ============================================== #
# === USER REGISTRATION AND AUTHENTIFICATION === #
# ============================================== #

@app.route("/account/auth", methods = ["POST"])
def auth() -> str:
    username = request.json.get('username')
    password = request.json.get('password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"msg": "Wrong login or password"}, 401

    expire_data = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = app.config["JWT_SECRET"], algorithm="HS256")
    return {"token": token}, 200


@app.route("/account/registration", methods = ["POST"])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user_object = {"username": username, "password": password, "waiting": False, "role": "user"}
    registration_access = app.config["REGISTRATION"]
    if db.users.find_one({"username": username, "waiting": True}):
        db.users.update_one({"username": username, "waiting": True}, {"$set": user_object})
        return {"msg": "Registration success"}, 200
    elif registration_access == "allowed":
        finded_user = db.users.find_one({"username": username})
        if finded_user:
            return {"msg": "Login already use"}, 401
        db.users.insert_one(user_object)
        return {"msg": "Registration success"}, 200
    elif registration_access == "on_request":
        # AND SOME CODE HERE ....
        # HERE NEED TO CREATE METHOD OR WRITE CODE 
        # WHO CREATE REQUEST FOR ADMIN AND MODERATORS
        pass
    return {"msg": "Registration forbidden"}, 401


@app.route("/account/addUserToQueue", methods = ["POST"])
@token_required
def add_to_register_queue():
    username = request.json.get("username")

    if current_user["role"] != "admin":
        return {"msg": "Registration forbidden"}; 401

    if db.users.find_one({"username": username}) is not None:
        return {"msg": "This login already use"}, 401
    
    db.users.insert_one({"username": username, "waiting": True})
    return {"msg": f"User <{username}> was created and waiting registration"}, 200



# ===================== #
# === COMMON ROUTES === #
# ===================== #

@app.route("/server/info", methods = ["POST"])
def get_server_info():
    return {"server_name": app.config["LSERVER_NAME"]}, 200



# ==================== #
# === IMAGE ROUTES === #
# ==================== #

# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/image/upload", methods = ["POST"])
@token_required
def upload_image():
    if 'image' not in request.files:
        return {"msg": "No file part"}, 401
    
    file = request.files['image']
    if file.filename == '':
        return {"msg": "No selected file"}, 401
    
    if file.filename.split(".")[-1] != "webp":
        return {"msg": "Wrong extension"}, 401

    image_bytes = request.files['image'].read()
    image_name = str(uuid.uuid4()) + ".webp"
    db.images.insert_one({"author": current_user["username"], "name": image_name, "image": image_bytes})
    return {"filename": image_name, "author": current_user["username"]}, 200


# ADD TOKEN AUTHORIZATION
@app.route("/image/info", methods = ["POST"])
@token_required
def image_info():
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if not image:
        return {"msg": "File dont exist"}, 401
    return {"author": image["author"], "image_name": image["name"]}, 200


# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/image/download", methods = ["POST"])
@token_required
def download_image():
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if image is None:
        return {"msg": "File does not exist"}, 401
    return send_file(io.BytesIO(image["image"]), mimetype="image/webp", download_name = "image.webp"), 200



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



# ===================== #
# === SYSTEM ROUTES === #
# ===================== #

@app.route("/gameSystem/create", methods = ["POST"])
@token_required
def create_system():
    data = request.json
    if not db.images.find_one({"name": data["image_name"]}):
        return {"msg": "Image does not exist"}, 401
    if not re.fullmatch("[0-9a-z\-_]+", data["codename"]):
        return {"msg": "Wrong codename"}, 401
    if db.structs.find_one({"author": current_user["username"], "codename": data["codename"], "type": "game_system"}):
        return {"msg": "Codename already taken"}, 401
    
    new_system = {
        "name": data["name"],
        "codename": data["codename"],
        "image_name": data["image_name"]
        }
    hash = hashlib.md5(str(new_system).encode()).hexdigest()
    new_system["type"] = "game_system"
    new_system["author"] = current_user["username"]
    new_system["hash"] = hash
    db.structs.insert_one(new_system)
    return {"hash": hash}, 200


@app.route("/gameSystem/get", methods = ["POST"])
@token_required
def get_system():
    codename = request.json.get("codename")
    if not codename:
        return {"msg": "Undefined system"}, 401
    system = db.structs.find_one({"type": "game_system", "codename": codename})
    if not system:
        return {"msg": "Undefined system"}, 401
    del system["type"]
    del system["_id"]
    #system["can_change"] = True if current_user["username"] == system["author"] else False
    return system, 200


@app.route("/gameSystem/getHash", methods = ["POST"])
@token_required
def get_system_hash():
    codename = request.json.get("codename")
    if not codename:
        return {"msg": "Undefined system"}, 401
    system = db.structs.find_one({"type": "game_system", "codename": codename})
    if not system:
        return {"msg": "Undefined system"}, 401
    return {"hash": system["hash"]}, 200


@app.route("/gameSystems/get", methods = ["POST"])
@token_required
def get_systems():
    data = request.json
    page = data.get("page", 0)
    systems = db.structs.find({"type": "game_system"}).skip(10 * page).limit(10)
    codenames = [el["codename"] for el in systems]
    return {"systems": codenames}, 200


@app.route("/gameSystems/getCount", methods = ["POST"])
@token_required
def get_systems_count():
    count = db.structs.count_documents({"type": "game_system"})
    return {"count": count}


@app.route("/gameSystems/delete", methods = ["POST"])
@token_required
def delete_system():
    if not request.json.get("codename", False):
        return {"msg": "Undefined codename"}, 401
    game_system = db.structs.find_one({"author": current_user["username"], "codename": request.json["codename"], "type": "game_system"})
    db.images.delete_one({"name": game_system["image_name"]})
    db.structs.delete_one(game_system)
    db.structs.delete_many({"type": "schema", "author": current_user["username"], "game_system": game_system["codename"]})
    return {"Ok": True}, 200



# ==================== #
# === TABLE ROUTES === #
# ==================== #


@app.route("/gameSystem/getTable", methods = ["POST"])
@token_required
def get_table():
    if not request.json.get("game_system", False) or not request.json.get("table_name", False):
        return {"msg": "\"Game system\" or \"Table name\" is undefined"}, 401
    schema = db.structs.find_one({"author": current_user["username"], "type": "schema", "codename": request.json["table_name"], "game_system": request.json["game_system"]})
    return {"table_data": schema["table_data"], "search_fields": schema["search_fields"], "table_fields": schema["table_fields"], "hash": schema["hash"]}, 200


@app.route("/gameSystem/getTableHash", methods = ["POST"])
@token_required
def get_table_hash():
    if not request.json.get("game_system", False) or not request.json.get("table_name", False):
        return {"msg": "\"Game system\" or \"Table name\" is undefined"}, 401
    schema = db.structs.find_one({"author": current_user["username"], "type": "schema", "codename": request.json["table_name"], "game_system": request.json["game_system"]})
    return {"hash": schema["hash"]}, 200


@app.route("/gameSystem/getTables", methods = ["POST"])
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


@app.route("/gameSystem/createTable", methods = ["POST"])
@token_required
def create_table():
    for property in ["common", "macros", "table", "properties"]:
        if property not in list(request.json.keys()):
            return {"msg": "Bad request"}, 401
    
    if not request.json["common"].get("table_codename", False) or not request.json["common"].get("table_name", False):
        return {"msg": "Not name or codename"}, 401
    
    table_hash = hashlib.md5(str(request.json).encode()).hexdigest()
    table_filter = {
        "type": "schema",
        "author": current_user["username"],
        "game_system": request.headers.get("Game-System"),
        "codename": request.json["common"]["table_codename"]
        }
    
    search_fields = [field.strip() for field in request.json.get("common", {}).get("search_fields", "").split(";")]

    if db.structs.find_one(table_filter):
        db.structs.update_one(table_filter, {
            "$set": {
                "name": request.json["common"]["table_name"],
                "hash": table_hash,
                "search_fields": search_fields,
                "table_data": request.json,
                "table_fields": get_fields(request.json["table"]),
                "icon": request.json["common"]["table_icon"]
            }
        })
    else:
        table = {
            "author": current_user["username"],
            "game_system": request.headers.get("Game-System"),
            "icon": request.json["common"].get("table_icon", ""),
            "name": request.json["common"]["table_name"],
            "codename": request.json["common"]["table_codename"],
            "hash": table_hash,
            "type": "schema",
            "search_fields": search_fields,
            "table_data": request.json,
            "table_fields": get_fields(request.json["table"])
        }
        db.structs.insert_one(table)
    return {"Ok": True, "hash": table_hash}, 200


@app.route("/gameSystem/deleteTable", methods = ["POST"])
@token_required
def delete_table():
    if not request.json.get("game_system", False) or not request.json.get("table_name", False):
        return {"msg": "\"Game system\" or \"Table name\" is undefined"}, 401
    db.structs.delete_one({"author": current_user["username"], "type": "schema", "codename": request.json["table_name"], "game_system": request.json["game_system"]})
    return {}, 200


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
#@token_required
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