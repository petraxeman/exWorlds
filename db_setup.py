import hashlib
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import pymongo.errors as errors


load_dotenv()

server_addr = input("MongoDB server address: ").strip()
mongo_admin_login = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_admin_passwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
mongo_exowrlds_login = os.getenv("MONGO_EXWORLDS_USERNAME")
mongo_exowrlds_passwd = os.getenv("MONGO_EXWORLDS_PASSWORD")
exworlds_admin_login = os.getenv("EXWORLDS_ADMIN_USERNAME")
exworlds_admin_password = os.getenv("EXWORLDS_ADMIN_PASSWORD")

salt = os.getenv("GLOBAL_PASSWORD_SALT")



print(f"Mongo exworlds database user: {mongo_exowrlds_login}")
print(f"Exworlds admin user {exworlds_admin_login}")


client = MongoClient(f"mongodb://{mongo_admin_login}:{mongo_admin_passwd}@{server_addr}/admin")

db = Database(client, "exworlds")
users = Collection(db, "users", create=True)
structs = Collection(db, "structs", create=True)
notes = Collection(db, "notes", create=True)
images = Collection(db, "images", create=True)


if not users.find_one({"username": "Server"}):
    users.insert_one({
        "username": "Server",
        "role": "server-admin",
        "info": {
            "server-name": "exWorlds",
            "custom-roles": {}
        }
    })


if not users.find_one({"username": exworlds_admin_login}):
    users.insert_one({
            "username": exworlds_admin_login,
            "password-hash": hashlib.pbkdf2_hmac("sha512", str(exworlds_admin_password).encode(), str(salt).encode(), 2 ** 8).hex(),
            "rights": ["any-create", "any-delete", "any-account", "cant-be-blocked"],
            "blocked": "",
            "waiting": {
                "registration": False,
                "approval": False
                },
            "relationship": {
                "black-list": []
                }
            })


try:
    client.exworlds.command("createUser", mongo_exowrlds_login, pwd=mongo_exowrlds_passwd, roles = [{"role": "readWrite", "db": "exworlds"}])
except errors.OperationFailure:
    pass
except Exception as err:
    print(err)


quit()