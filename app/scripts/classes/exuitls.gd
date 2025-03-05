extends Node
class_name EXUtils



static func array_to_color(arr: Array) -> Color:
	if arr.size() == 3:
		return Color(arr[0], arr[1], arr[2])
	elif arr.size() == 4:
		return Color(arr[0], arr[1], arr[2], arr[3])
	return Color(0, 0, 0)


static func apply_theme(node: Node, specific_zone: String = ""):
	var awaiting: Array = [node]
	while awaiting:
		var current_node = awaiting.pop_at(0)
		if current_node.has_method("get_children"):
			var new_children = current_node.get_children()
			if new_children:
				awaiting += new_children
		
		if current_node.has_meta("can_apply_theme") and current_node.get_meta("can_apply_theme", false):
			current_node._apply_theme()
		
		var applying_themes: Array = []
		var expected: String = ""
		var zone: String = specific_zone if specific_zone else Globals.current_theme.active_zone
		match current_node.get_class():
			"Button":
				expected = "stylebox"
				applying_themes = [
					["default", "button/normal", "normal"],
					["default", "button/hover", "hover"],
					["default", "button/pressed", "pressed"],
					["default", "button/desabled", "desabled"]
					]
				if current_node.has_meta("extheme_class"):
					var extheme_class: String = current_node.get_meta("extheme_class")
					applying_themes += [
						[zone, "%s/normal" % extheme_class, "normal"],
						[zone, "%s/hover" % extheme_class, "hover"],
						[zone, "%s/pressed" % extheme_class, "pressed"], 
						[zone, "%s/desabled" % extheme_class, "desabled"]
						]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					var mode: String = theme_class[2]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override(mode, Globals.current_theme.get_resource_for(lzone, cls, expected))
				continue
			"TextureRect":
				expected = "texture"
				applying_themes = [["default", "background"]]
				if current_node.has_meta("extheme_class"):
					applying_themes += [[zone, current_node.get_meta("extheme_class")]]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.texture = Globals.current_theme.get_resource_for(lzone, cls, expected)
			"PanelContainer":
				expected = "stylebox"
				applying_themes = [["default", "content-panel"]]
				if current_node.has_meta("extheme_class"):
					applying_themes += [[zone, current_node.get_meta("extheme_class")]]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override("panel", Globals.current_theme.get_resource_for(lzone, cls, expected))
			"Window", "ConfirmationDialog":
				expected = "stylebox"
				applying_themes = [["default", "subwindow-border"]]
				if current_node.has_meta("extheme_class"):
					applying_themes += [[zone, current_node.get_meta("extheme_class")]]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_stylebox_override("embedded_border", Globals.current_theme.get_resource_for(lzone, cls, expected))
						current_node.add_theme_stylebox_override("embedded_unfocused_border", Globals.current_theme.get_resource_for(lzone, cls, expected))
			"Label":
				expected = "color"
				applying_themes = [["default", "label/font-color"]]
				if current_node.has_meta("extheme_class"):
					applying_themes += [[zone, "%s/font-color" % current_node.get_meta("extheme_class")]]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_color_override("font_color", Globals.current_theme.get_resource_for(lzone, cls, "font-color"))
				
				expected = "font"
				applying_themes = [["default", "label/font"]]
				if current_node.has_meta("extheme_class"):
					applying_themes += [[zone, "%s/font" % current_node.get_meta("extheme_class")]]
				
				for theme_class in applying_themes:
					var lzone: String = theme_class[0]
					var cls: String = theme_class[1]
					
					if Globals.current_theme.is_resource_exsits(lzone, cls):
						current_node.add_theme_font_override("font", Globals.current_theme.get_resource_for(lzone, cls, "font"))
				
static func disconnect_all(node: Node):
	for conn in node.get_incoming_connections():
		node.disconnect(conn["signal"], conn["callable"])

static func disconnect_all_pressed(node: Button):
	for conn in node.pressed.get_connections():
		node.pressed.disconnect(conn["callable"])
