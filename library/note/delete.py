from typing import Union
from library import utils, contpath



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not utils.verify_access(
        sender["uid"], sender["rights"],
        {"server-admin", "any-create"},
        (pack["owner"], *pack["redactors"])):

        return {"msg": "You can't do that"}, 401
    
    db.execute("DELETE FROM notes WHERE path = %s", (path.to_note,))
    
    return {"msg": "Note delete success"}