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


func _compile_resources():
	for key in raw_resources:
		if raw_resources[key].has("inherit"):
			var child: Dictionary = raw_resources[key]
			var parent: Dictionary = raw_resources.get(child["inherit"]).duplicate()
			if not parent:
				continue
			child.erase("action"); child.erase("inherit")
			parent.merge(child, true)
			raw_resources[key] = parent


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
		
		match raw_resources[key].get("type", "nothing"):
			"image":
				resources[key] = _build_image(value.get("path", "res://assets/images/placeholder.svg"))
			"gradient":
				resources[key] = _build_gradient(value)
			"color-texture":
				resources[key] = _build_color_texture(value)
			"stylebox":
				resources[key] = _build_stylebox(value)
			"label-font":
				resources[key] = _build_label_font(value)
			"button-font":
				resources[key] = _build_button_font(value)


func _build_image(path: String):
	return {"data": load(_adapt_path(path)), "to": "texture"}


func _build_gradient(settings: Dictionary):
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
	
	return {"data": texture, "to": "texture"}


func _build_color_texture(settings: Dictionary):
	var texture: GradientTexture1D = GradientTexture1D.new()
	texture.gradient = Gradient.new()
	texture.gradient.colors = PackedColorArray([EXUtils.array_to_color(settings["color"])])
	
	return {"data": texture, "to": "texture"}


func _build_stylebox(settings: Dictionary):
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
	
	return {"data": stylebox, "to": "stylebox"}


func _build_label_font(settings: Dictionary):
	var new_settings: Array = []
	for key in settings:
		match key:
			"font":
				new_settings.append({"data": load(_adapt_path(settings[key])), "mode": "font", "to": "font"})
			"font-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_color", "to": "color"})
			"shadow-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_shadow_color", "to": "color"})
			"outline-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_outline_color", "to": "color"})
			"shadow-offset":
				new_settings.append({"data": settings[key][0], "mode": "shadow_offset_x", "to": "constant"})
				new_settings.append({"data": settings[key][1], "mode": "shadow_offset_y", "to": "constant"})
			"outline-size":
				new_settings.append({"data": settings[key], "mode": "outline_size", "to": "constant"})
			"shadow-outline-size":
				new_settings.append({"data": settings[key], "mode": "shadow_outline_size", "to": "constant"})
	return new_settings


func _build_button_font(settings: Dictionary):
	var new_settings: Array = []
	for key in settings:
		match key:
			"font":
				new_settings.append({"data": load(_adapt_path(settings[key])), "mode": "font", "to": "font"})
			"font-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_color", "to": "color"})
			"hover-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_hover_color", "to": "color"})
			"pressed-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_pressed_color", "to": "color"})
			"disabled-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_disabled_color", "to": "color"})
			"outline-color":
				new_settings.append({"data": EXUtils.array_to_color(settings[key]), "mode": "font_outline_color", "to": "color"})
			"font-size":
				new_settings.append({"data": settings[key], "mode": "font_size", "to": "font-size"})
			"outline-size":
				new_settings.append({"data": settings[key], "mode": "outline_size", "to": "constant"})
	return new_settings


func _adapt_path(raw_path: String):
	var points = raw_path.split("://")
	if len(points) > 1:
		if points[0] == "theme":
			return path_to_theme + "/" + points[1]
	return raw_path


func set_zone(zone: String):
	active_zone = zone
	_parse_res_names()
	_load_resources()


func is_resource_exist(codename: String, zone: String = ""):
	if not zone:
		zone = active_zone
	return resources.has(zones.get(zone, {}).get(codename, ""))


func get_resource(codename: String, zone: String = ""):
	if not zone:
		zone = active_zone
	return resources[zones[zone][codename]]


func apply_theme(node: Node):
	var awaiting: Array = [node]
	while awaiting:
		var current_node = awaiting.pop_at(0)
		
		if current_node.has_method("get_children"):
			awaiting += current_node.get_children()
		
		if current_node.get_meta("extheme_skip", false):
			continue
		
		if current_node.has_method("_apply_theme"):
			current_node._apply_theme()
		
		var theme_classes: Dictionary = {}
		var zone: String = Globals.current_theme.active_zone
		var extheme_class: String = current_node.get_meta("extheme_class", "")
		match current_node.get_class():
			"Button":
				theme_classes = {
					"default":[
						{"loader": "standart", "data": ["default", "button/normal"], "mode": "normal", "to": "stylebox"}, 
						{"loader": "standart", "data": ["default", "button/hover"], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "button/pressed"], "mode": "pressed", "to": "stylebox"}, 
						{"loader": "standart", "data": ["default", "button/disabled"], "mode": "disabled", "to": "stylebox"},
						{"loader": "unpack", "data": ["default", "button/font"]}
						],
					"specific": [
						{"loader": "standart", "data": [zone, "%s/normal" % extheme_class], "mode": "normal", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/hover" % extheme_class], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/pressed" % extheme_class], "mode": "pressed", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/disabled" % extheme_class], "mode": "disabled", "to": "stylebox"},
						{"loader": "unpack", "data": [zone, "%s/font" % extheme_class]}
						]
					}
			"OptionButton":
				theme_classes = {
					"default":[
						{"loader": "standart", "data": ["default", "option/normal"], "mode": "normal", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "option/hover"], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "option/pressed"], "mode": "pressed", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "option/disabled"], "mode": "disabled", "to": "stylebox"},
						{"loader": "unpack", "data": ["default", "option/font"]}
					],
					"specific": [
						{"loader": "standart", "data": [zone, "%s/normal" % extheme_class], "mode": "normal", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/hover" % extheme_class], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/pressed" % extheme_class], "mode": "pressed", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/disabled" % extheme_class], "mode": "disabled", "to": "stylebox"},
						{"loader": "unpack", "data": [zone, "%s/font" % extheme_class]}
					]
				}
			"TextureRect":
				theme_classes = {
					"default": [{"loader": "standart", "data": ["default", "texturerect/texture"], "mode": "texture", "to": "texture"}],
					"specific": [{"loader": "standart", "data": [zone, "%s/texture" % extheme_class], "mode": "texture", "to": "texture"}]
					}
			"PanelContainer":
				theme_classes = {
					"default": [{"loader": "standart", "data": ["default", "container/panel"], "mode": "panel", "to": "stylebox"}],
					"specific": [{"loader": "standart", "data": [zone, "%s/panel" % extheme_class], "mode": "panel", "to": "stylebox"}]
					}
			"Window", "ConfirmationDialog":
				theme_classes = {
					"default": [{"loader": "standart", "data": ["default", "subwindow/border"], "mode": "embedded_border", "to": "stylebox"}],
					"specific": [{"loader": "standart", "data": [zone, "%s/border" % extheme_class], "mode": "embedded_border", "to": "stylebox"}]
					}
			"PopupMenu":
				theme_classes = {
					"default": [
						{"loader": "standart", "data": ["default", "popup/panel"], "mode": "panel", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "popup/hover"], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "popup/separator"], "mode": "separator", "to": "stylebox"},
						],
					"specific": [
						{"loader": "standart", "data": [zone, "%s/panel" % extheme_class], "mode": "panel", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/hover" % extheme_class], "mode": "hover", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/separator" % extheme_class], "mode": "separator", "to": "stylebox"},
						]
					}
			"Label":
				theme_classes = {
					"default": [{"loader": "unpack", "data": ["default", "label/font"]}],
					"specific": [{"loader": "unpack", "data": [zone, "%s/font" % extheme_class]}]
					}
			"LineEdit":
				theme_classes = {
					"default": [
						{"loader": "standart", "data": ["default", "lineedit/normal"], "mode": "normal", "to": "stylebox"},
						{"loader": "standart", "data": ["default", "lineedit/focus"], "mode": "focus", "to": "stylebox"}
						],
					"specific": [
						{"loader": "standart", "data": [zone, "%s/normal" % extheme_class], "mode": "normal", "to": "stylebox"},
						{"loader": "standart", "data": [zone, "%s/focus" % extheme_class], "mode": "focus", "to": "stylebox"}
						]
					}
			_:
				continue
		
		for i in theme_classes["specific"].size():
			var resource: Dictionary
			
			if is_resource_exist(theme_classes["specific"][i]["data"][1], theme_classes["specific"][i]["data"][0]):
				resource = theme_classes["specific"][i]
				
			elif is_resource_exist(theme_classes["default"][i]["data"][1], theme_classes["default"][i]["data"][0]):
				resource = theme_classes["default"][i]
			else:
				continue
			
			var resources_to_apply: Array = []
			match resource["loader"]:
				"standart":
					resource["data"] = get_resource(resource["data"][1], resource["data"][0])["data"]
					resources_to_apply.append(resource)
				"unpack":
					resources_to_apply += get_resource(resource["data"][1], resource["data"][0])
			
			for res in resources_to_apply:
				match res["to"]:
					"stylebox":
						current_node.add_theme_stylebox_override(res["mode"], res["data"])
					"font":
						current_node.add_theme_font_override(res["mode"], res["data"])
					"font-size":
						current_node.add_theme_font_size_override(res["mode"], res["data"])
					"constant":
						current_node.add_theme_constant_override(res["mode"], res["data"])
					"color":
						current_node.add_theme_color_override(res["mode"], res["data"])
					"texture":
						current_node.texture = res["data"]


static func load_from_dir(path: String) -> ExworldsTheme:
	if not FileAccess.file_exists(path + "/theme.json"):
		return
	
	var config_file: FileAccess = FileAccess.open(path + "/theme.json", FileAccess.READ)
	var config_dict: Dictionary = JSON.parse_string(config_file.get_as_text())
	
	return ExworldsTheme.new(path, config_dict)
