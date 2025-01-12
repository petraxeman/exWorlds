from typing import Union
from library import search_utils


def process(db, data: dict, sender: dict) -> Union[dict, int]:
    #if not data.get("type", ""):
    #    return {"msg": "Type undefined"}, 401
    
    #pack_type = data.get("type")
    page = int(data.get("page", 1))

    if page < 1:
        return {"msg": "Wrong page range"}, 401
    
    query = """
    WITH user_favorites AS (
        SELECT
            ARRAY(SELECT jsonb_array_elements_text(lists->'favorites')) AS favorite_paths
        FROM users
        WHERE uid = %(user_uid)s
    ),
    filtered_packs AS (
        SELECT *
        FROM packs
        WHERE
        (
            NOT hidden OR
            owner = %(user_uid)s OR 
            %(user_uid)s = ANY(redactors) OR
            'server-admin' = ANY(ARRAY(SELECT rights FROM users WHERE uid = %(user_uid)s))
        )
    )
    SELECT filtered_packs.*
    FROM filtered_packs
    LEFT JOIN user_favorites
    ON filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY['']))
    ORDER BY
        filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY[''])) DESC,
        filtered_packs.likes DESC
    LIMIT %(limit)s OFFSET %(offset)s;
    """
        
    path_list = db.fetchall(query, {"user_uid": sender["uid"], "limit": 10, "offset": 10 * (page - 1)})

    if not path_list:
        return {"msg": "Undefined packs"}
    
    return {"paths": path_list}, 200