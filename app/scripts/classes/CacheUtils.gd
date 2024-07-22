extends Node
class_name CacheUtils



static func init_cache_db(server_addr: String):
	server_addr = server_addr.replace(".", "-")
	var db_path: String = "user://cache/{0}.db".format([server_addr])
	var cache = SQLite.new()
	
	var cold_start: bool = false
	if not FileAccess.file_exists(db_path):
		cold_start = true
	
	cache.path = db_path
	cache.open_db()
	if cold_start:
		var images_cache_schema = {
			"id": {"data_type": "int", "primary_key": true, "not_null": true},
			"filename": {"data_type": "text", "not_null": true},
			"image": {"data_type": "blob", "not_null": true}
		}
		var req_cache_structs = {
			"id": {"data_type": "int", "primary_key": true, "not_null": true},
			"hash": {"data_type": "text", "not_null": true},
			"request": {"data_type": "text", "not_null": true},
			"data": {"data_type": "text", "not_null": true}
		}
		cache.drop_table("images")
		cache.drop_table("contents")
		cache.create_table("images", images_cache_schema)
		cache.create_table("contents", req_cache_structs)
	return cache


static func get_image(filename: String) -> Dictionary:
	var cached: Array = Global.cache.select_rows("images", 'filename="{0}"'.format([filename]), ["file_name", "image"])
	if cached != []:
		var loaded_image = Image.new()
		var _error = loaded_image.load_webp_from_buffer(cached[0]["image"])
		return {"exists": true, "image": loaded_image}
	return {"exists": false}


static func put_image(filename: String, image: Image) -> void:
	Global.cache.insert_row("images", {"filename": filename, "image": image.save_webp_to_buffer(true)})


static func get_content(request: String) -> Dictionary:
	var cached: Array = Global.cache.select_rows("contents", 'request="{0}"'.format([request]), ["hash", "data"])
	if cached != []:
		var loaded_data: Dictionary = JSON.parse_string(cached[0]["data"])
		return {"exists": true, "hash": cached[0]["hash"], "data": loaded_data}
	return {"exists": false}


static func put_content(request: String, hash: String, data: Dictionary, action: String) -> void:
	pass
