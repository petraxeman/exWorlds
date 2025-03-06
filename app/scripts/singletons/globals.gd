extends Node

const exworlds_version: String = "v0.0.1"

var current_theme_codename: String = "petraxeman.exworlds.default"

var loaded_themes: Array = []
var current_theme: ExworldsTheme

var server_list: Dictionary = {}
var current_server: Dictionary


func _ready():
	_load_config()
	_load_themes()
	
	_post_loading()


func set_theme(theme_codename: String) -> bool:
	for ltheme in loaded_themes:
		if ltheme.codename == theme_codename:
			current_theme = ltheme
			return true
	return false


func _load_config():
	if not FileAccess.file_exists("user://config.json"):
		_save_config()
	
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.READ)
	var config_dict: Dictionary = JSON.parse_string(config_file.get_as_text())
	
	current_theme_codename = config_dict["current_theme_codename"]
	server_list = config_dict["server_list"]


func _save_config():
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.WRITE)
	config_file.store_string(JSON.stringify(
		{
			"current_theme_codename": current_theme_codename,
			"server_list": server_list
		}
	))


func _load_themes():
	if not DirAccess.dir_exists_absolute("user://themes"):
		DirAccess.make_dir_absolute("user://themes")
	
	loaded_themes.append(ExworldsTheme.load_from_dir("res://assets/default_theme"))
	for theme_folder in DirAccess.get_directories_at("user://themes"):
		var etheme: ExworldsTheme = ExworldsTheme.load_from_dir("user://themes/" + theme_folder)
		loaded_themes.append(etheme)


func _post_loading():
	set_theme(current_theme_codename)
