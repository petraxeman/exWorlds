from typing import Union
from library import utils, contpath



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    options = data.get("options", {})
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    if not pack:
        return {"msg": "Pack not found."}, 401
    
    if not utils.verify_access(
        sender["uid"], sender["rights"],
        {"delete-pack", "any-delete", "server-admin"},
        (pack["owner"],)
        ):
        return {"msg": "You can't do that."}, 401
    
    delete_pack(db, pack, options)    
    return {"msg": f"System {path.to_pack} deleted."}, 200



def delete_pack(db, pack: dict, options: dict) -> bool:
    if options.get("delete-poster", True):
        db.execute("DELETE FROM images WHERE codename = %s", (pack["image_name"],))

    db.execute("DELETE FROM packs WHERE path = %s", (pack["path"],))

    db.execute("""
        UPDATE users
        SET lists = jsonb_set(
            jsonb_set(
                lists,
                '{favorites}',
                (lists->'favorites') - %(path_to_remove)s,
                true
            ),
            '{likes}',
            (lists->'likes') - %(path_to_remove)s,
            true
        ) WHERE %(path_to_remove)s = ANY(
            ARRAY(
                SELECT jsonb_array_elements_text(lists->'favorites')
                UNION
                SELECT jsonb_array_elements_text(lists->'likes')
            )
        );
    """, {"path_to_remove": pack["path"]})
    
    db.execute("DELETE FROM tables WHERE starts_with(path, %s)", (pack["path"],))
    db.execute("DELETE FROM notes WHERE starts_with(path, %s)", (pack["path"],))

    return True