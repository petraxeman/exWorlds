from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    page = int(data.get("page", 1))
    search_query = str(data.get("search", ""))
    
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
            starts_with(path, 'gc:')
        ) AND (
            NOT hidden OR
            owner = %(user_uid)s OR 
            %(user_uid)s = ANY(redactors) OR
            'server-admin' = ANY(ARRAY(SELECT rights FROM users WHERE uid = %(user_uid)s))
        )
    )"""

    if search_query:
        query += """
        SELECT filtered_packs.*
        FROM filtered_packs
        LEFT JOIN user_favorites
        ON filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY['']))
        ORDER BY
            filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY[''])) DESC,
            similarity(filtered_packs.search_field, %(search_query)s) DESC
        LIMIT %(limit)s OFFSET %(offset)s;
        """
    else:
        query += """
        SELECT filtered_packs.*
        FROM filtered_packs
        LEFT JOIN user_favorites
        ON filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY['']))
        ORDER BY
            filtered_packs.path = ANY(COALESCE(user_favorites.favorite_paths, ARRAY[''])) DESC,
            filtered_packs.likes DESC
        LIMIT %(limit)s OFFSET %(offset)s;
        """
    
    path_list = db.fetchall(query, {"user_uid": sender["uid"], "limit": 10, "offset": 10 * (page - 1), "search_query": search_query})

    path_list = [pack["path"] for pack in path_list or []]

    return {"paths": path_list}, 200