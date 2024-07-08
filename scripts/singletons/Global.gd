extends Node

var servers = []



func _ready():
	load_config()

func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_config()
		get_tree().quit()

func load_config():
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.READ)
	if config_file == null:
		_init_config_file()
		config_file = FileAccess.open("user://server_config.json", FileAccess.READ)
	var config_data: String = config_file.get_as_text()
	var config = JSON.parse_string(config_data)
	servers = config["servers"]

func save_config():
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.WRITE)
	var data = {
		"servers": servers
	}
	config_file.store_string(JSON.stringify(data))

func add_server(server_name: String, server_address: String):
	servers.append({"name": server_name, "address": server_address, "can_del": true})

func remove_server(index: int):
	servers.remove_at(index)

func _init_config_file():
	var config_file: FileAccess = FileAccess.open("user://server_config.json", FileAccess.WRITE)
	var data = {
		"servers": [{"name": "Local server", "address": "localhost", "can_del": false}]
	}
	config_file.store_string(JSON.stringify(data))
	config_file.close()
