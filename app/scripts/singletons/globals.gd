extends Node

const exworlds_version: String = "v0.0.1"

var server_list: Dictionary = {}
var current_server: Dictionary

var locale: String = "ru" :
	set (value):
		TranslationServer.set_locale(value)
		locale = value



func _ready():
	_pre_loading()
	_load_config()


func _pre_loading():
	if not DirAccess.dir_exists_absolute("user://temp"):
		DirAccess.make_dir_absolute("user://temp")
	else:
		EXUtils.clear_temp()


func _load_config():
	if not FileAccess.file_exists("user://config.json"):
		_save_config()
	
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.READ)
	var config_dict: Dictionary = JSON.parse_string(config_file.get_as_text())
	
	ThemeHandler.set_theme(config_dict["current_theme_codename"])
	server_list = config_dict["server_list"]
	locale = config_dict.get("locale", "ru")


func _save_config():
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.WRITE)
	config_file.store_string(JSON.stringify(
		{
			"current_theme_codename": ThemeHandler.current_theme.codename,
			"server_list": server_list,
			"locale": locale
		}
	))
