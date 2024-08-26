def validator_add_user_to_queue(db, required_username: str, sender_role: str, required_role: str = "user")  -> bool:
    if required_username != "":
        username = required_username
    else:
        return {"ok": False}
    
    role = "nobody" if required_role == "" else required_role
    
    if sender_role != "admin" and sender_role != "server-admin":
        return {"ok": False}
    
    if db.users.find_one({"username": username}) is not None:
        return {"ok": False}
    
    return {"ok": True, "username": username, "role": role}


def register_user(db, username: str, user_document: dict) -> bool:
    if db.users.find_one({"username": username}):
        return False
    db.users.insert_one(user_document)
    return True


def register_request(db, username: str, user_document: dict) -> bool:
    if  db.users.find_one({"username": username}):
        return False
    user_document["waiting"]["approval"] = True
    user_document["role"] = "user"
    db.users.insert_one(user_document)
    return True


def build_user(reference: dict):
    return {
        "username": reference["username"],
        "password-hash": reference.get("password-hash", ""),
        "role": reference.get("role", "user"),
        "waiting": {
            "registration": reference.get("waiting", {}).get("registration", False),
            "approval": reference.get("waiting", {}).get("approval", False)
            },
        "black-list": reference.get("friends", {}).get("black-list", [])
    }