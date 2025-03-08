extends Node

var finded_themes: Dictionary = {}
var current_theme: ExworldsTheme



func _ready():
	_find_themes()


func set_theme(theme_codename: String):
	_load_theme(theme_codename)
	

func _find_themes():
	if not DirAccess.dir_exists_absolute("user://themes"):
		DirAccess.make_dir_absolute("user://themes")
	
	var theme_pathes: Array = ["res://assets/default_theme"] 
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
	
