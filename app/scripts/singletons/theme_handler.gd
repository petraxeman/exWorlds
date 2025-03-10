extends Node

var finded_themes: Dictionary = {}
var current_theme: ExworldsTheme



func _ready():
	_init_themes()
	_find_themes()


func _init_themes():
	if not DirAccess.dir_exists_absolute("user://themes"):
		DirAccess.make_dir_absolute("user://themes")
	
	# WARNING NEED TO CHANGE AFTER WORK WITH THEMES WILL DONE
	#if not DirAccess.get_directories_at("user://themes") or not DirAccess.dir_exists_absolute("user://themes/default_theme"):
		#EXUtils.copy_directory_recursively("res://assets/default_theme", "user://themes/default_theme")


func set_theme(theme_codename: String):
	_load_theme(theme_codename)


func _find_themes():
	# WARNING NEED TO CHANGE AFTER WORK WITH THEMES WILL DONE
	var theme_pathes: Array = ["res://assets/default_theme"]
	#var theme_pathes: Array = []
	for theme_folder in DirAccess.get_directories_at("user://themes"):
		theme_pathes.append("user://themes/%s" % theme_folder)
	
	for theme_path in theme_pathes:
		if not FileAccess.file_exists("%s/manifest.json" % theme_path):
			continue
		
		var manifest: FileAccess = FileAccess.open("%s/manifest.json" % theme_path, FileAccess.READ)
		var data: Dictionary = JSON.parse_string(manifest.get_as_text())
		
		data["path"] = theme_path
		if not data.get("codename"):
			continue
		
		finded_themes[data["codename"]] = data


func _load_theme(theme_codename: String):
	if not finded_themes.has(theme_codename):
		theme_codename = "petraxeman.exworlds.default"
	current_theme = ExworldsTheme.load_from_dir(finded_themes[theme_codename]["path"])
	
