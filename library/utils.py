import hashlib
import os
from typing import Any



def get_password_hash(password: str, salt: str) -> str:
    #salt = os.getenv("PASSWORD_SALT")
    return hashlib.pbkdf2_hmac("sha512", str(password).encode(), str(salt).encode(), 2 ** 8).hex()


def get_hash(text: str) -> str:
    return hashlib.md5(str(text).encode()).hexdigest()


def spath_to_dpath(spath: str) -> dict:
    exp, points = spath.strip().split("://")
    points = points.split("/")
    return {"exp": exp.strip(), "points": points}


def dpath_to_spath(dpath: dict) -> str:
    return dpath["exp"] + "://" + "/".join(dpath.points)


def get_by_path(db, spath: str) -> dict:
    if not validate_path(spath):
        return {}
    
    exp, _ = spath.strip().split("://")
    match exp:
        case "pack":
            return db.packs.find_one({"path": spath})
        case "table":
            return db.tables.find_one({"path": spath})


def table_to_pack(spath: str):
    exp, points = spath.split("://")
    points = points.split("/")
    
    match len(points):
        case 3:
            return "addon://" + "/".join(points[:2])
        case _:
            return "game-system://" + "/".join(points[:1])


def validate_path(spath: str) -> bool:
    try:
        exp, points = spath.strip().split("://")
        points = points.split("/")
        if 0 > len([p for p in points if p != ""]) > 4:
            raise Exception("Too long or too small path.")
        if exp == "":
            raise Exception("Expection is not defined.")
        return True
    except:
        return False