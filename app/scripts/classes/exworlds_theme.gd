extends Node
class_name ExworldsTheme

var codename: String = ""
var visible_name: String = ""
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
	_compile_resources()
	
	visible_name = config.get("visible-name", "Undefined name")
	codename = config["codename"]
	zones = config.get("zones", {})
	
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
			"color":
				return Color(1, 1, 1)
			"font":
				return {"font": FontFile.new()}
	return resources[zones[zone][property]]


func is_resource_exsits(zone: String, property: String) -> bool:
	if not resources.get(zones.get(zone, {}).get(property)):
		return false
	return true


func _parse_res_names():
	if not default_res_names:
		for key in zones["default"]:
			default_res_names.append(zones["default"][key])
	
	specific_res_names = []
	if active_zone != "default":
		for key in zones[active_zone]:
			specific_res_names.append(zones[active_zone][key])


func _load_resources():
	var res_names = default_res_names + specific_res_names
	resources = {}
	for key in res_names:
		if not key in raw_resources:
			raw_resources[key] = null
			continue
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
			"make_font":
				resources[key] = make_font(value)


func _compile_resources():
	for key in raw_resources:
		if raw_resources[key].has("inherit"):
			var child: Dictionary = raw_resources[key]
			var parent: Dictionary = raw_resources.get(child["inherit"]).duplicate()
			print(parent)
			if not parent:
				continue
			child.erase("action"); child.erase("inherit")
			parent.merge(child, true)
			raw_resources[key] = parent


func load_image(path: String):
	return load(path)


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
	
	var content_margin = settings.get("cont-margin", [-1, -1, -1, -1])
	stylebox.content_margin_left = content_margin[0]
	stylebox.content_margin_top = content_margin[1]
	stylebox.content_margin_right = content_margin[2]
	stylebox.content_margin_bottom = content_margin[3]
	
	stylebox.border_color = EXUtils.array_to_color(settings.get("bord-color", [0.8, 0.8, 0.8])) 
	
	var border_width = settings.get("border-width", [0, 0, 0, 0])
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


func make_font(settings: Dictionary):
	var new_settings: Dictionary = {}
	if settings.get("font"):
		new_settings["font"] = load(_adapt_path(settings.get("font")))
	if settings.get("font-color"):
		new_settings["font-color"] = EXUtils.array_to_color(settings.get("font-color"))
	if settings.get("shadow-color"):
		new_settings["shadow-color"] = EXUtils.array_to_color(settings.get("shadow-color"))
	if settings.get("outline-color"):
		new_settings["outline-color"] = EXUtils.array_to_color(settings.get("outline-color"))
	if settings.get("shadow-offset"):
		new_settings["shadow-offset-x"] = settings.get("shadow-offset")[0]
		new_settings["shadow-offset-y"] = settings.get("shadow-offset")[1]
	if settings.get("outline-size"):
		new_settings["outline-size"] = settings.get("outline-size")
	if settings.get("shadow-outline-size"):
		new_settings["shadow-outline-size"] = settings.get("shadow-outline-size")
	return new_settings


func _adapt_path(raw_path: String):
	var points = raw_path.split("://")
	if len(points) > 1:
		if points[0] == "theme":
			return path_to_theme + "/" + points[1]
	return raw_path


static func apply_theme(node: Node, specific_zone: String = ""):
	var awaiting: Array = [node]
	while awaiting:
		var current_node = awaiting.pop_at(0)
		if current_node.get_meta("extheme_skip", false):
			continue
		
		if current_node.has_method("get_children"):
			awaiting += current_node.get_children()
		
		if current_node.get_meta("can_apply_theme", false):
			current_node._apply_theme()
		
		var applying_classes: Array = []
		var expected: String = ""
		var zone: String = specific_zone if specific_zone else Globals.current_theme.active_zone
		var extheme_class: String = current_node.get_meta("extheme_class", "")
		match current_node.get_class():
			"Button":
				expected = "stylebox"
				applying_classes = [["default", "button/normal", "normal"], ["default", "button/hover", "hover"],
									["default", "button/pressed", "pressed"], ["default", "button/desabled", "desabled"]]
				if extheme_class:
					applying_classes += [[zone, "%s/normal" % extheme_class, "normal"], [zone, "%s/hover" % extheme_class, "hover"],
										[zone, "%s/pressed" % extheme_class, "pressed"], [zone, "%s/desabled" % extheme_class, "desabled"]]
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]; var mode: String = theme_class[2]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override(mode, Globals.current_theme.get_resource_for(lzone, cls, expected))
			"TextureRect":
				expected = "texture"
				applying_classes = [["default", "texturerect/texture"]]
				if extheme_class:
					applying_classes += [[zone, extheme_class + "/texture"]]
				
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.texture = Globals.current_theme.get_resource_for(lzone, cls, expected)
			"PanelContainer":
				expected = "stylebox"
				applying_classes = [["default", "container/panel"]]
				if extheme_class:
					applying_classes += [[zone, extheme_class + "/panel"]]
				
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override("panel", Globals.current_theme.get_resource_for(lzone, cls, expected))
			"Window", "ConfirmationDialog":
				expected = "stylebox"
				applying_classes = [["default", "subwindow/border"]]
				if extheme_class:
					applying_classes += [[zone, extheme_class + "/border"]]
				
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override("embedded_border", Globals.current_theme.get_resource_for(lzone, cls, expected))
						current_node.add_theme_stylebox_override("embedded_unfocused_border", Globals.current_theme.get_resource_for(lzone, cls, expected))
			"Label":
				expected = "font"
				applying_classes = [["default", "label/font"]]
				if extheme_class:
					applying_classes = [[zone, extheme_class + "/font"]]
				
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						var font_settings: Dictionary = Globals.current_theme.get_resource_for(lzone, cls, expected)
						var cn: Label = Label.new()
						
						current_node.add_theme_font_override("font", font_settings.get("font", current_node.get_theme_font("font")))
						
						current_node.add_theme_color_override("font_color", font_settings.get("font-color", current_node.get_theme_color("font_color")))
						current_node.add_theme_color_override("font_outline_color", font_settings.get("outline-color", current_node.get_theme_color("font_outline_color")))
						current_node.add_theme_color_override("font_shadow_color", font_settings.get("shadow-color", current_node.get_theme_color("font_shadow_color")))
						
						current_node.add_theme_constant_override("outline_size", font_settings.get("outline-size", current_node.get_theme_constant("outline_size")))
						current_node.add_theme_constant_override("shadow_outline_size", font_settings.get("shadow-outline-size", current_node.get_theme_constant("shadow_outline_size")))
						
						current_node.add_theme_constant_override("shadow_offset_x", font_settings.get("shadow-offset-x", current_node.get_theme_constant("shadow_offset_x")))
						current_node.add_theme_constant_override("shadow_offset_y", font_settings.get("shadow-offset-y", current_node.get_theme_constant("shadow_offset_y")))
			"LineEdit":
				expected = "stylebox"
				applying_classes = [["default", "lineedit/normal", "normal"], ["default", "lineedit/focus", "focus"]]
				if extheme_class:
					applying_classes += [[zone, extheme_class + "/normal", "normal"], [zone, extheme_class + "/focus", "focus"]]
				for theme_class in applying_classes:
					var lzone: String = theme_class[0]; var cls: String = theme_class[1]; var mode: String = theme_class[2]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override(mode, Globals.current_theme.get_resource_for(lzone, cls, expected))
	
	
static func load_from_dir(path: String) -> ExworldsTheme:
	if not FileAccess.file_exists(path + "/theme.json"):
		return
	
	var config_file: FileAccess = FileAccess.open(path + "/theme.json", FileAccess.READ)
	var config_dict: Dictionary = JSON.parse_string(config_file.get_as_text())
	
	return ExworldsTheme.new(path, config_dict)
