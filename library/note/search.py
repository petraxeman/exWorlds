from typing import Union
from library import utils



def by_path(db, data: dict, sender: dict) -> Union[tuple, int]:
    if not data.get("path-list", []):
        return {"msg": "Pathes undefined."}, 401
    
    pack_cache = {}
    notes = []
    
    for path in data.get("path-list"):
        pack_path = utils.path_back(path)

        if pack_path not in pack_cache.keys():
            pack = db.execute("SELECT * FROM packs WHERE path = %s", (utils.path_back(path)))
            if pack:
                if pack["hidden"]:
                    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and "server-admin" in sender["rights"]:
                        pack_cache[pack["path"]] = False
                    else:
                        pack_cache[pack["path"]] = True
                else:
                    pack_cache[pack["path"]] = True
            else:
                pack_cache[pack["path"]] = False
        
        if pack_cache[pack_path] == True:
            notes.append(db.fetchone("SELECT * FROM notes WHERE path = %s", (path,)))        
    
    if not notes:
        return {"msg": "Notes not found."}, 401
    
    return {"notes": notes}


def by_query(db, data: dict, sender: dict) -> Union[tuple, int]:
    pass