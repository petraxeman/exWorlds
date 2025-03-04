extends Control

var server_item_scene: PackedScene = load("res://scenes/server_selection/server_item.tscn")



func _ready():
	Globals.current_theme.active_zone = "server-selection"
	EXUtils.apply_theme(self)
	
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
	EXUtils.apply_theme(self)
	return
	$background.texture = Globals.current_theme.get_resource_for("server-selection", "background", "texture")

func _on_exit_pressed() -> void:
	get_tree().quit()
