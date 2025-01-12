import os
import library.utils
import psycopg2.extras

from flask import Flask

from dotenv import load_dotenv, dotenv_values

from library.dbext import Postgres
from library.auth.api import bp as api_auth_bp
from library.common.api import bp as api_common_bp
from library.pack.api import bp as api_pack_bp
from library.image.api import bp as api_image
from library.table.api import bp as api_table

load_dotenv()
psycopg2.extras.register_uuid()
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)



db = Postgres()

def create_app():
    app: Flask = Flask(__name__)
    app.config.from_mapping(dotenv_values())
    app.config["version"] = "Active Beta"
    
    # MODULES INITIALS
    db.init_app(app)

    with app.app_context():
        app.register_blueprint(api_auth_bp)
        app.register_blueprint(api_common_bp)
        app.register_blueprint(api_pack_bp)
        app.register_blueprint(api_image)
        app.register_blueprint(api_table)
    return app



#import server.route