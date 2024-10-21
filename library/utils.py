import hashlib
import os
from typing import Any



def get_password_hash(password: str, salt: str) -> str:
    #salt = os.getenv("PASSWORD_SALT")
    return hashlib.pbkdf2_hmac("sha512", str(password).encode(), str(salt).encode(), 2 ** 8).hex()


def get_hash(text: str) -> str:
    return hashlib.md5(str(text).encode()).hexdigest()


def get_by_path(db, path: dict) -> dict:
    expected = path.get("exp", "")
    points = path.get("points", [])
    if not validate_path(path):
        return None
    
    if not is_use_addon(path):
        match expected:
            case "pack":
                return db.packs.find_one({"codename": points[0], "reference": {}, "type": "game-system"})
            case "table":
                return db.tables.find_one({"codename": points[1], "reference.points": [points[0]], "reference.exp": "pack"})
    else:
        match expected:
            case "pack":
                return db.packs.find_one({"codename": points[1], "reference": {"points": [points[0]], "exp": "pack"}, "type": "addon"})
            case "table":
                return db.tables.find_one({"codename": points[1], "reference": {"points": [points[0], points[1]], "exp": "pack"}})
    return None


def path_up(path: dict):
    match path["exp"]:
        case "pack":
            return path
        case "table":
            return {"points": [*path["points"][:-1]], "exp": "pack"}


def validate_path(path: dict) -> bool:
    if not path.get("points", []) or not path.get("exp"):
        return False
    
    if 0 > len(path.get("points", [])) > 4:
        return False
    
    if path.get("exp", "") not in ("pack", "table", "card"):
        return False
    
    return True


def is_use_addon(path: dict):
    expected_length = {"pack": 1, "table": 2, "card": 3}
    if expected_length[path["exp"]] == len(path["points"]):
        return False
    return True