extends Node

var servers = []
var active_server: int = -1
var timer: Timer = Timer.new()


func _ready():
	load_config()
	timer.one_shot = false
	timer.wait_time = 1
	timer.timeout.connect(_on_timer_timeout)


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_config()
		get_tree().quit()


#func auth(username: String, password: String) -> bool:
#	return false


func token_renew() -> bool:
	var http = HTTPRequest.new()
	var headers = ["token:" + servers[active_server]["token"]]
	http.request("http://" + servers[active_server]["address"] + "/umapi/renew", headers, HTTPClient.METHOD_POST)
	var result = await http.request_completed
	if result[1] != 200:
		return false
	var data = JSON.parse_string(result[3].get_string_from_utf8())
	if data.get("result", 100) != 1:
		return false
	servers[active_server]["token"] = data["tokne"]
	servers[active_server]["token_ttl"] = data["token_ttl"]
	return true


func check_token_ttl():
	if active_server == -1:
		return
	var time_left: float = servers[active_server]["token_ttl"] - Time.get_unix_time_from_system() < 30
	if time_left < 0:
		get_tree().quit()
	elif time_left < 30:
		token_renew()


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
	servers.append({"name": server_name, "address": server_address, "can_del": true, "token": "", "token_ttl": 0})


func remove_server(index: int):
	servers.remove_at(index)


func _init_config_file():
	var config_file: FileAccess = FileAccess.open("user://server_config.json", FileAccess.WRITE)
	var data = {
		"servers": []
	}
	config_file.store_string(JSON.stringify(data))
	config_file.close()


func _on_timer_timeout():
	check_token_ttl()
