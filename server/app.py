from flask import Flask
from flask_redis import FlaskRedis
from flask_pymongo import PyMongo
import os



app: Flask = Flask(__name__)

app.config["REDIS_URL"] = "redis://localhost:6379/0"
app.config["MONGO_URI"] = "mongodb://devuser:devpasswd@localhost:27017/main"

app.config["REGISTRATION"] = "on_request" # allowed
app.config["LSERVER_NAME"] = "PupiDupi"
redis_client = FlaskRedis(app)
db = PyMongo(app).db



import server.route