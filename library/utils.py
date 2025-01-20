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


def spath_back(spath: str, direction: int = "pack") -> str:
    lengths = ["table", "note"]
    exp, points = spath.split("://")
    points = points.split("/")
    if direction == "game-system":
        return exp + "://" + points[0]
    elif direction == "pack":
        if len(points) == 1 + (lengths.index(exp) + 1):
            return exp + "://" + points[0]
        elif len(points) == 2 + (lengths.index(exp) + 1):
            return exp + "://" + points[:2]
    elif direction == "table":
        if len(points) == 1 + (lengths.index(exp) + 1):
            return exp + "://" + points[:2]
        elif len(points) == 2 + (lengths.index(exp) + 1):
            return exp + "://" + points[:3]


def get_by_path(db, spath: str) -> dict:
    exp, points = spath.split("://")
    match exp:
        case "game-system":
            return db.fetchone("SELECT * FROM packs WHERE path = %s", (spath,))
        case "addon":
            return db.fetchone("SELECT * FROM packs WHERE path = %s", (spath,))
        case "table":
            return db.fetchone("SELECT * FROM tables WHERE path = %s", (spath,))
        case "note":
            pass
    return {}


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