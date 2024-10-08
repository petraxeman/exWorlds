import datetime
import io
import uuid
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app,
    send_file
    )

bp = Blueprint("api-images", __name__)



@bp.route("/api/image/upload", methods = ["POST"])
@token_required
def upload_image():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user
    
    if 'image' not in request.files:
        return {"msg": "No file part"}, 401
    
    file = request.files['image']
    if file.filename == '':
        return {"msg": "No selected file"}, 401
    
    if file.filename.split(".")[-1] != "webp":
        return {"msg": "Wrong extension"}, 401

    username = current_user["username"]
    image_date = datetime.datetime.now().strftime("%H%M%d%m%y")
    image_uuid = str(uuid.uuid4())
    image_name = f"{username}-{image_date}-{image_uuid}.webp"

    image_bytes = request.files['image'].read()
    db.images.insert_one({"owner": current_user["username"], "name": image_name, "image": image_bytes})
    return {"filename": image_name, "owner": current_user["username"]}, 200


@bp.route("/api/image/download", methods = ["POST"])
@token_required
def download_image():
    db = current_app.config["MONGODB_INST"]
    
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if image is None:
        return {"msg": "File does not exist"}, 401
    return send_file(io.BytesIO(image["image"]), mimetype="image/webp", download_name = image["name"]), 200


@bp.route("/api/image/delete", methods = ["POST"])
@token_required
def delete_image():
    db = current_app.config["MONGODB_INST"]
    current_user = request.current_user

    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})

    if image is None:
        return {"msg": "File does not exist"}, 401
    
    if current_user["username"] != image["owner"] and (current_user["role"] not in ["admin", "server-admin"]):
        return {"msg": "You can't do that"}, 401
    
    db.images.delete_one({"name": filename})

    return {"msg": f"File deleted <{filename}>"}, 200