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



@bp.route("/image/upload", methods = ["POST"])
@token_required
def upload_image():
    db = current_app.config["MNOGODB_INST"]
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


@bp.route("/image/info", methods = ["POST"])
@token_required
def image_info():
    db = current_app.config["MNOGODB_INST"]
    
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if not image:
        return {"msg": "File dont exist"}, 401
    
    return {"owner": image["owner"], "image_name": image["name"]}, 200


@bp.route("/image/download", methods = ["POST"])
@token_required
def download_image():
    db = current_app.config["MNOGODB_INST"]
    
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if image is None:
        return {"msg": "File does not exist"}, 401
    return send_file(io.BytesIO(image["image"]), mimetype="image/webp", download_name = image["name"]), 200