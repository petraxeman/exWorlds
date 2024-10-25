from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    path = data.get("path", "")
    if not path:
        return {"msg": "Path undefined."}, 401
    
    pack = db.packs.find_one({"path": path})
    if not pack:
        return {"msg": "Pack not found."}, 401
    
    existed_rights = {"delete-pack", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["username"] != pack["owner"] and (not existed_rights):
        return {"msg": "You can't do that."}, 401
    
    try:
        assert delete_pack(db, pack)
    except Exception as err:
        print(err)
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    return {"msg": f"System {path} deleted."}, 200


def delete_pack(db, pack: dict) -> bool:
    db.images.delete_one({"name": pack["image-name"]})
    db.packs.delete_one(pack)
    delete_from_likes(db, pack["path"])
    delete_from_favorite(db, pack["path"])
    return True


def delete_from_likes(db, path: str):
    db.users.update_many({"lists.likes": path}, {"$pull": {"lists.likes": path}})
    

def delete_from_favorite(db, path: str):
    db.users.update_many({"lists.favorites": path}, {"$pull": {"lists.favorites": path}})