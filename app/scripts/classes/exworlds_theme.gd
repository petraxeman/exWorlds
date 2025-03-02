extends Node
class_name ExworldsTheme

var path_to_theme: String = ""
var resources: Dictionary = {}
var zones: Dictionary = {}
var codename: String = ""



func _init(path: String, config: Dictionary):
	path_to_theme = path
	_parse_resources(config.get("resources", {}))
	codename = config["codename"]
	zones = config["zones"]


func get_resource_for(zone: String, property: String):
	return resources[zones[zone][property]]


func _parse_resources(res: Dictionary):
	for key in res:
		match res[key].get("action", "nothing"):
			"load_image":
				resources[key] = load(_adapt_path(res[key].get("value", "res://assets/images/placeholder.svg")))
			"load_gradient":
				var grt: GradientTexture2D = GradientTexture2D.new()
				grt.fill_from = Vector2(res[key]["from"][0], res[key]["from"][1])
				grt.fill_to = Vector2(res[key]["to"][0], res[key]["to"][1])
				
				var colors = []
				for color in res[key]["colors"]:
					var clr = Color(color[0], color[1], color[2])
					colors.append(clr)
				
				grt.gradient = Gradient.new()
				grt.gradient.offsets = PackedFloat32Array(res[key]["offsets"])
				grt.gradient.colors = PackedColorArray(colors)
				
				resources[key] = grt
			"load_plain_color":
				var grt: GradientTexture1D = GradientTexture1D.new()
				grt.gradient = Gradient.new()
				grt.gradient.colors = PackedColorArray([Color(res[key]["color"][0], res[key]["color"][1], res[key]["color"][2])])
				
				resources[key] = grt


func _adapt_path(raw_path: String):
	var points = raw_path.split("://")
	if len(points) > 1:
		if points[0] == "theme":
			return path_to_theme + "/" + points[1]
	return raw_path


static func load_from_dir(path: String) -> ExworldsTheme:
	if not FileAccess.file_exists(path + "/config.json"):
		return
	
	var config_file: FileAccess = FileAccess.open(path + "/config.json", FileAccess.READ)
	var config_dict: Dictionary = JSON.parse_string(config_file.get_as_text())
	
	return ExworldsTheme.new(path, config_dict)
