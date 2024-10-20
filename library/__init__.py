import os
import library.utils

from flask import Flask
from flask_pymongo import PyMongo

from dotenv import load_dotenv

from library.auth.api import bp as api_auth_bp
from library.common.api import bp as api_common_bp
from library.pack.api import bp as api_pack_bp
from library.image.api import bp as api_image
from library.table.api import bp as api_table

load_dotenv()

mongo: PyMongo = PyMongo()

def create_app():
    app: Flask = Flask(__name__)
    
    # PRE CONFIG INITIALS
    app.config["MONGO_URI"] = "mongodb://devu:devp@localhost:27017/exworlds"
    app.config["JWT_SECRET"] = "03lh6fhrl3pa91f2oyov4syba65sjwvemshe2-5xn1mv1wfhxa4v-mxtrzm6dvy-3dum8xd1awb1atqa1oy8cspv3p7zynoic6cf"
    app.config["REGISTRATION"] = "allowed"
    app.config["PASSWORD_SALT"] = os.getenv("GLOBAL_PASSWORD_SALT")
    app.config["TOKEN_SALT"] = os.getenv("GLOBAL_TOKEN_SALT")

    # MODULES INITIALS
    mongo.init_app(app)

    # POST CONFIG INITIALS
    app.config["MONGODB_INST"] = mongo.db

    with app.app_context():
        app.register_blueprint(api_auth_bp)
        app.register_blueprint(api_common_bp)
        app.register_blueprint(api_pack_bp)
        app.register_blueprint(api_image)
        app.register_blueprint(api_table)
    return app



#import server.route