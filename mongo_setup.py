from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import pymongo.errors as errors

server_addr = input("MongoDB server address: ").strip()
mongo_admin_login = input("MongoDB admin login: ").strip()
mongo_admin_passwd = input("MongoDB admin password: ").strip()
print()
mongo_exowrlds_login = input("MongoDB exowrlds db login: ").strip()
mongo_exowrlds_passwd = input("MongoDB exowrlds db password: ").strip()
print()
mongo_app_login = input("MongoDB exowrlds app login: ").strip()
mongo_app_password = input("MongoDB exowrlds app login: ").strip()
print()


client = MongoClient(f"mongodb://{mongo_admin_login}:{mongo_admin_passwd}@{server_addr}/admin")

db = Database(client, "exworlds")
users = Collection(db, "users", create=True)
structs = Collection(db, "structs", create=True)
notes = Collection(db, "notes", create=True)
images = Collection(db, "images", create=True)

try:
    client.exworlds.command("createUser", mongo_exowrlds_login, pwd=mongo_exowrlds_passwd, roles = [{"role": "readWrite", "db": "main"}])
except errors.OperationFailure:
    pass
except Exception as err:
    print(err)

users.insert_one({"username": mongo_app_login, "password": mongo_app_password, "await": False, "role": "admin"})

quit()