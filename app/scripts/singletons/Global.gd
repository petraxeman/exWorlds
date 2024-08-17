extends Node

var servers: Array            = []
var active_server_index: int  = -1
var active_server: Dictionary
var cache: CacheLib = CacheLib.new()
var proto: String = "http"



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	load_config()
	var dir: DirAccess = DirAccess.open("user://")
	if not dir.dir_exists("cache"):
		dir.make_dir("cache")


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_config()
		get_tree().quit()



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func auth(username: String, password: String) -> bool:
	var data: Dictionary = {"username": username, "password": password}
	var result: Dictionary = await UrlLib.post("auth", [], data, "json", false)
	if not result["Ok"]:
		return false
	servers[active_server_index]["token"] = result["token"]
	active_server = servers[active_server_index]
	return true


func register(username: String, password: String) -> bool:
	var data: Dictionary = {"username": username, "password": password}
	var result: Dictionary = await UrlLib.post("registration", [], data, "json", false)
	if not result["Ok"]:
		return false
	return true


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


func base64URL_decode(input: String) -> PackedByteArray:
	match (input.length() % 4):
		2: input += "=="
		3: input += "="
	return Marshalls.base64_to_raw(input.replacen("_","/").replacen("-","+"))


func get_current_user():
	var splited_token = active_server["token"].split(".")
	var decoded_payload = base64URL_decode(splited_token[1]).get_string_from_utf8()
	return JSON.parse_string(decoded_payload)



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
