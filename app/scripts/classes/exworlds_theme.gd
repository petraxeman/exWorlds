extends Node
class_name ExworldsTheme

var codename: String = ""
var path_to_theme: String = ""

var active_zone: String = "default"
var resources: Dictionary = {}
var zones: Dictionary = {}



func _init(path: String, config: Dictionary):
	path_to_theme = path
	_parse_resources(config.get("resources", {}))
	codename = config["codename"]
	zones = config["zones"]


func get_resource_for(zone: String, property: String, expect: String):
	if not resources.get(zones.get(zone, {}).get(property)):
		match expect:
			"texture":
				return GradientTexture1D.new()
			"stylebox":
				return StyleBoxFlat.new()
	return resources[zones[zone][property]]


func is_resource_exsits(zone: String, property: String) -> bool:
	if not resources.get(zones.get(zone, {}).get(property)):
		return false
	return true


func _parse_resources(res: Dictionary):
	for key in res:
		match res[key].get("action", "nothing"):
			"load_image":
				resources[key] = load(_adapt_path(res[key].get("value", "res://assets/images/placeholder.svg")))
			"make_gradient":
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
			"make_plain_color":
				var grt: GradientTexture1D = GradientTexture1D.new()
				grt.gradient = Gradient.new()
				grt.gradient.colors = PackedColorArray([Color(res[key]["color"][0], res[key]["color"][1], res[key]["color"][2])])
				
				resources[key] = grt
			"make_stylebox":
				var sb = StyleBoxFlat.new()
				var corner_radius = res[key].get("corner", [0, 0, 0, 0])
				sb.corner_radius_top_left = corner_radius[0]
				sb.corner_radius_top_right = corner_radius[1]
				sb.corner_radius_bottom_left = corner_radius[2]
				sb.corner_radius_bottom_right = corner_radius[3]
				
				sb.bg_color = EXUtils.array_to_color(res[key].get("color"))
				
				var content_margin = res[key].get("cont_margins", [-1, -1, -1, -1])
				sb.content_margin_left = content_margin[0]
				sb.content_margin_top = content_margin[1]
				sb.content_margin_right = content_margin[2]
				sb.content_margin_bottom = content_margin[3]
				
				sb.border_color = EXUtils.array_to_color(res[key].get("bord_color", [0.8, 0.8, 0.8])) 
				
				var border_width = res[key].get("border_width", [0, 0, 0, 0])
				sb.border_width_left = border_width[0]
				sb.border_width_top = border_width[1]
				sb.border_width_right = border_width[2]
				sb.border_width_bottom = border_width[3]
				
				resources[key] = sb


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
