extends Control

var server_item_scene: PackedScene = load("res://scenes/server_selection/server_item.tscn")



func _ready():
	_apply_theme()
	
	$content/actions/panel/margin/vbox/name/version.text = Globals.exworlds_version
	$content/actions/panel/margin/vbox/name/title.text = tr("EXWORLDS_TITLE")
	$content/actions/panel/margin/vbox/buttons/delete.text = tr("SERVER_SELECTION_DELETE")
	$content/actions/panel/margin/vbox/buttons/add_server.text = tr("SERVER_SELECTION_ADD_SERVER")
	$content/actions/panel/margin/vbox/buttons/theme_editor.text = tr("SERVER_SELECTION_THEME_EDITOR")
	$content/actions/panel/margin/vbox/buttons/settings.text = tr("SERVER_SELECTION_SETTINGS")
	$content/actions/panel/margin/vbox/buttons/exit.text = tr("SERVER_SELECTION_EXIT")
	
	render_server_list()


func render_server_list():
	for child in $content/server_list/panel/maegin/scroll/server_list.get_children():
		child.queue_free()
	
	if not Globals.server_list:
		var lbl: Label = Label.new()
		lbl.text = tr("SERVER_SELECTION_NO_SERVERS")
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		$content/server_list/panel/maegin/scroll/server_list.add_child(lbl)
		$content/server_list/panel/maegin/scroll/server_list.alignment = BoxContainer.ALIGNMENT_CENTER
	else:
		for serv in Globals.server_list:
			var serv_item = server_item_scene.instantiate()
			serv_item.setup(
				serv.get("server-name", ""),
				serv.get("mark", ""),
				serv["addr"],
				serv_item.CANT_CONNECT,
				serv["uuid"]
				)
			serv_item.selected.connect(select_server)
			$content/server_list/panel/maegin/scroll/server_list.add_child(serv_item)


func select_server(uuid: String):
	for child in $content/server_list/panel/maegin/scroll/server_list.get_children():
		if child.uuid == uuid:
			child.is_selected = true
		else:
			child.is_selected = false
		child._apply_theme()
	print("uuid %s" % uuid)


func _apply_theme():
	$background.texture = Globals.current_theme.get_resource_for("server-selection", "background", "texture")
	
	for child in $content/actions/panel/margin/vbox/buttons.get_children():
		if Globals.current_theme.is_resource_exsits("default", "button/normal"):
			child.add_theme_stylebox_override("normal", Globals.current_theme.get_resource_for("default", "button/normal", "stylebox"))
		if Globals.current_theme.is_resource_exsits("default", "button/hover"):
			child.add_theme_stylebox_override("hover", Globals.current_theme.get_resource_for("default", "button/hover", "stylebox"))
		if Globals.current_theme.is_resource_exsits("default", "button/pressed"):
			child.add_theme_stylebox_override("pressed", Globals.current_theme.get_resource_for("default", "button/pressed", "stylebox"))
		if Globals.current_theme.is_resource_exsits("default", "button/disabled"):
			child.add_theme_stylebox_override("disabled", Globals.current_theme.get_resource_for("default", "button/disabled", "stylebox"))
		
	if Globals.current_theme.is_resource_exsits("server-selection", "play-button/normal"):
		$content/actions/panel/margin/vbox/buttons/enter.add_theme_stylebox_override("normal", Globals.current_theme.get_resource_for("server-selection", "play-button/normal", "stylebox"))
	if Globals.current_theme.is_resource_exsits("server-selection", "play-button/hover"):
		$content/actions/panel/margin/vbox/buttons/enter.add_theme_stylebox_override("hover", Globals.current_theme.get_resource_for("server-selection", "play-button/hover", "stylebox"))
	if Globals.current_theme.is_resource_exsits("server-selection", "play-button/pressed"):
		$content/actions/panel/margin/vbox/buttons/enter.add_theme_stylebox_override("pressed", Globals.current_theme.get_resource_for("server-selection", "play-button/pressed", "stylebox"))
	if Globals.current_theme.is_resource_exsits("server-selection", "play-button/disabled"):
		$content/actions/panel/margin/vbox/buttons/enter.add_theme_stylebox_override("disabled", Globals.current_theme.get_resource_for("server-selection", "play-button/disabled", "stylebox"))


func _on_exit_pressed() -> void:
	get_tree().quit()
