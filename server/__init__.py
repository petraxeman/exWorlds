from flask import Flask
from flask_redis import FlaskRedis
from flask_pymongo import PyMongo
import os



app: Flask = Flask(__name__)

app.config["REDIS_URL"] = "redis://localhost:6379/0"
app.config["MONGO_URI"] = "mongodb://devu:devp@localhost:27017/exworlds"
app.config["JWT_SECRET"] = "03lh6fhrl3pa91f2oyov4syba65sjwvemshe2-5xn1mv1wfhxa4v-mxtrzm6dvy-3dum8xd1awb1atqa1oy8cspv3p7zynoic6cf"
app.config["REGISTRATION"] = "allowed"              # allowed - In concept, on_reques - required, forbidden - required
app.config["LSERVER_NAME"] = "PupiDupi"

redis_client = FlaskRedis(app)
db = PyMongo(app).db



import server.route