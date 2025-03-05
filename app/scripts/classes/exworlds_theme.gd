extends Node
class_name ExworldsTheme

var codename: String = ""
var path_to_theme: String = ""

var active_zone: String = "default"

var raw_resources: Dictionary = {}
var default_res_names: Array = []
var specific_res_names: Array = []

var resources: Dictionary = {}
var zones: Dictionary = {}



func _init(path: String, config: Dictionary):
	path_to_theme = path
	raw_resources = config.get("resources", {})
	codename = config["codename"]
	zones = config["zones"]
	_parse_res_names()


func set_zone(zone: String):
	active_zone = zone
	_parse_res_names()
	_load_resources()
	

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


func _parse_res_names():
	if not default_res_names:
		for key in zones["default"]:
			default_res_names.append(zones["default"][key])
	
	if active_zone != "default":
		for key in zones[active_zone]:
			specific_res_names.append(zones[active_zone][key])


func _load_resources():
	var res_names = default_res_names + specific_res_names
	for key in res_names:
		var value: Dictionary = raw_resources[key]
		match raw_resources[key].get("action", "nothing"):
			"load_image":
				resources[key] = load_image(_adapt_path(value.get("path", "res://assets/images/placeholder.svg")))
			"make_gradient":
				resources[key] = make_gradient(value)
			"make_plain_color":
				resources[key] = make_plain_color(value)
			"make_stylebox":
				resources[key] = make_stylebox(value)


func load_image(path: String):
	return load(_adapt_path(path))


func make_gradient(settings: Dictionary):
	var texture: GradientTexture2D = GradientTexture2D.new()
	texture.fill_from = Vector2(settings["from"][0], settings["from"][1])
	texture.fill_to = Vector2(settings["to"][0], settings["to"][1])
	
	var colors = []
	for color in settings["colors"]:
		var clr = EXUtils.array_to_color(color)
		colors.append(clr)
	
	texture.gradient = Gradient.new()
	texture.gradient.offsets = PackedFloat32Array(settings["offsets"])
	texture.gradient.colors = PackedColorArray(colors)
	
	return texture


func make_plain_color(settings: Dictionary):
	var texture: GradientTexture1D = GradientTexture1D.new()
	texture.gradient = Gradient.new()
	texture.gradient.colors = PackedColorArray([EXUtils.array_to_color(settings["color"])])
	
	return texture


func make_stylebox(settings: Dictionary):
	var stylebox = StyleBoxFlat.new()
	var corner_radius = settings.get("corner", [0, 0, 0, 0])
	stylebox.corner_radius_top_left = corner_radius[0]
	stylebox.corner_radius_top_right = corner_radius[1]
	stylebox.corner_radius_bottom_left = corner_radius[2]
	stylebox.corner_radius_bottom_right = corner_radius[3]
	
	stylebox.bg_color = EXUtils.array_to_color(settings.get("color"))
	
	var content_margin = settings.get("cont_margins", [-1, -1, -1, -1])
	stylebox.content_margin_left = content_margin[0]
	stylebox.content_margin_top = content_margin[1]
	stylebox.content_margin_right = content_margin[2]
	stylebox.content_margin_bottom = content_margin[3]
	
	stylebox.border_color = EXUtils.array_to_color(settings.get("bord_color", [0.8, 0.8, 0.8])) 
	
	var border_width = settings.get("border_width", [0, 0, 0, 0])
	stylebox.border_width_left = border_width[0]
	stylebox.border_width_top = border_width[1]
	stylebox.border_width_right = border_width[2]
	stylebox.border_width_bottom = border_width[3]
	
	var expand_margin = settings.get("expand", [0, 0, 0, 0])
	stylebox.expand_margin_left = expand_margin[0]
	stylebox.expand_margin_top = expand_margin[1]
	stylebox.expand_margin_right = expand_margin[2]
	stylebox.expand_margin_bottom = expand_margin[3]
	
	return stylebox

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
