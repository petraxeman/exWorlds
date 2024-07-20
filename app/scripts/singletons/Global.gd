extends Node

var servers: Array            = []
var active_server_index: int  = -1
var active_server: Dictionary
var cache: SQLite



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	IP.resolve_hostname("localhost", IP.TYPE_IPV4)
	load_config()
	_init_db()


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_config()
		get_tree().quit()



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func auth(username: String, password: String) -> bool:
	var headers: Array = ["Content-Type: application/json"]
	var data: String = JSON.stringify({"username": username, "password": password})
	ResLoader.http.request(UrlEnum.build("http", active_server["address"], "auth"), headers, HTTPClient.METHOD_POST, data)
	var result: Array = await ResLoader.http.request_completed
	if result[1] != 200:
		return false
	result[3] = JSON.parse_string(result[3].get_string_from_utf8())
	servers[active_server_index]["token"] = result[3]["token"]
	active_server = servers[active_server_index]
	return true


func register(username: String, password: String) -> bool:
	var data: String = JSON.stringify({"username": username, "password": password})
	var headers: Array = ["Content-Type: application/json"]
	ResLoader.http.request(UrlEnum.build("http", active_server["address"], "registration"), headers, HTTPClient.METHOD_POST, data)
	var result = await ResLoader.http.request_completed
	if not result[1] == 200:
		return false
	return true


func get_auth_data() -> Dictionary:
	return {
		"addr": active_server["address"], 
		"headers": ["Content-Type: application/json", "Auth-Token: " + active_server["token"]]
		}


func load_config():
	var config_exists: bool = FileAccess.file_exists("user://server_config.json")
	if config_exists == false:
		_init_config_file()
	
	var config_file = FileAccess.open("user://server_config.json", FileAccess.READ)
	var config_data: String = config_file.get_as_text()
	var config = JSON.parse_string(config_data)
	servers = config["servers"]


func save_config():
	var config_file: FileAccess = FileAccess.open("user://server_config.json", FileAccess.WRITE)
	var data = {
		"servers": servers
	}
	config_file.store_string(JSON.stringify(data))


func add_server(server_name: String, server_address: String):
	servers.append({"name": server_name, "address": server_address, "can_del": true, "token": ""})


func remove_server(index: int):
	servers.remove_at(index)


func set_active_server(index: int) -> bool:
	if index > servers.size():
		return false
	active_server_index = index
	active_server = servers[index]
	return true

# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _init_config_file():
	var config_file: FileAccess = FileAccess.open("user://server_config.json", FileAccess.WRITE)
	var data = {
		"servers": []
	}
	config_file.store_string(JSON.stringify(data))
	config_file.close()


func _init_db():
	cache = SQLite.new()
	cache.path = "user://cache.db"
	cache.open_db()
	
	var images_cache_schema = {
		"id": {"data_type": "int", "primary_key": true, "not_null": true},
		"author": {"data_type": "text", "not_null": true},
		"file_name": {"data_type": "text", "not_null": true},
		"image": {"data_type": "blob", "not_null": true}
	}
	var req_cache_structs = {
		"id": {"data_type": "int", "primary_key": true, "not_null": true},
		"hash": {"data_type": "text", "not_null": true},
		"data": {"data_type": "text", "not_null": true}
	}
	cache.drop_table("images")
	cache.drop_table("requests")
	cache.create_table("images", images_cache_schema)
	cache.create_table("requests", req_cache_structs)
