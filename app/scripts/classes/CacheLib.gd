extends Node
class_name CacheLib

var cache: SQLite



func _init():
	var db_path: String = "user://cache.db"
	cache = SQLite.new()
	
	var cold_start: bool = false
	if not FileAccess.file_exists(db_path):
		cold_start = true
	
	cache.path = db_path
	cache.open_db()
	if cold_start:
		cache.drop_table("images")
		cache.drop_table("contents")
		cache.create_table("images", {
			"id": {"data_type": "int", "primary_key": true, "not_null": true},
			"filename": {"data_type": "text", "not_null": true},
			"image": {"data_type": "blob", "not_null": true}
		})
		cache.create_table("contents", {
			"id": {"data_type": "int", "primary_key": true, "not_null": true},
			"hash": {"data_type": "text", "not_null": false},
			"address": {"data_type": "text", "not_null": true},
			"data": {"data_type": "text", "not_null": true}
		})


func get_image(filename: String) -> Dictionary:
	var request_filename = "server:{0};filename:{1}".format([Global.active_server["address"], filename])
	var response: Array = cache.select_rows("images", 'filename="{0}"'.format([request_filename]), ["filename", "image"])
	if response != []:
		var loaded_image = Image.new()
		var _error = loaded_image.load_webp_from_buffer(response[0]["image"])
		return {"Ok": true, "image": loaded_image}
	return {"Ok": false}


func put_image(filename: String, image: Image) -> void:
	var request_filename = "server:{0};filename:{1}".format([Global.active_server["address"], filename])
	cache.insert_row("images", {"filename": request_filename, "image": image.save_webp_to_buffer(true)})


func get_content(address: String) -> Dictionary:
	var request_address = "server:{0};content_marks:{1}".format([Global.active_server["address"], address])
	var response: Array = cache.select_rows("contents", 'address="{0}"'.format([request_address]), ["hash", "data"])
	if response != []:
		var loaded_data: Dictionary = JSON.parse_string(response[0]["data"])
		return {"Ok": true, "hash": response[0]["hash"], "data": loaded_data}
	return {"Ok": false}


func put_content(address: String, content_hash: String, data: Dictionary, update: bool = false) -> void:
	var request_address = "server:{0};content_marks:{1}".format([Global.active_server["address"], address])
	if update:
		cache.update_rows("contents", 'address="{0}"'.format([request_address]), {"hash": content_hash, "data": JSON.stringify(data)})
	cache.insert_row("contents", {"address": request_address, "hash": content_hash, "data": JSON.stringify(data)})
