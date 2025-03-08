extends Node

const exworlds_version: String = "v0.0.1"

var current_theme_codename: String = "petraxeman.exworlds.default"
var loaded_themes: Dictionary = {}
var current_theme: ExworldsTheme

var server_list: Dictionary = {}
var current_server: Dictionary

var locale: String = "ru" :
	set (value):
		TranslationServer.set_locale(value)
		locale = value



func _ready():
	_pre_loading()
	
	_load_config()
	_load_themes()
	
	_post_loading()


func set_theme(theme_codename: String):
	current_theme_codename = theme_codename
	if loaded_themes.has(theme_codename):
		current_theme = loaded_themes.get(theme_codename)
	
	if not current_theme:
		current_theme_codename = "petraxeman.exworlds.default"
		set_theme("petraxeman.exworlds.default")


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
	
	current_theme_codename = config_dict["current_theme_codename"]
	server_list = config_dict["server_list"]
	locale = config_dict.get("locale", "ru")


func _save_config():
	var config_file: FileAccess = FileAccess.open("user://config.json", FileAccess.WRITE)
	config_file.store_string(JSON.stringify(
		{
			"current_theme_codename": current_theme_codename,
			"server_list": server_list,
			"locale": locale
		}
	))


func _load_themes():
	if not DirAccess.dir_exists_absolute("user://themes"):
		DirAccess.make_dir_absolute("user://themes")
	
	loaded_themes = {}
	var theme: ExworldsTheme = ExworldsTheme.load_from_dir("res://assets/default_theme")
	loaded_themes[theme.codename] = theme
	for theme_folder in DirAccess.get_directories_at("user://themes"):
		
		theme = ExworldsTheme.load_from_dir("user://themes/" + theme_folder)
		loaded_themes[theme.codename] = theme


func _post_loading():
	set_theme(current_theme_codename)
