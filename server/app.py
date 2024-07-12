from flask import Flask
from flask_redis import FlaskRedis
from flask_pymongo import PyMongo
import os

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

app: Flask = Flask(__name__)
redis_client = FlaskRedis(app)
mongo = PyMongo(app, url = "mongodb://localhost:6380/mydb")

import server.route