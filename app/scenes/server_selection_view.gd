extends Control

var server_item_scene: PackedScene = load("res://scenes/server_selection/server_item.tscn")
var settings_view: PackedScene = load("res://scenes/settings_view.tscn")
var selected_server: String = ""


func _ready():
	_render()
	$server_delete_confirm/margin/content/actions/Cancel.pressed.connect(func(): $server_delete_confirm.hide())


func _render():
	Globals.current_theme.set_zone("server-selection")
	Globals.current_theme.apply_theme(self)
	_render_server_settings_subwin()
	_render_server_deletion_subwin()
	_render_server_list()


func _render_server_list():
	for child in $content/server_list/panel/maegin/scroll/server_list.get_children():
		child.queue_free()
	
	if not Globals.server_list:
		var lbl: Label = Label.new()
		lbl.text = tr("SERVER_SELECTION_NO_SERVERS")
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		$content/server_list/panel/maegin/scroll/server_list.add_child(lbl)
		$content/server_list/panel/maegin/scroll/server_list.alignment = BoxContainer.ALIGNMENT_CENTER
	else:
		$content/server_list/panel/maegin/scroll/server_list.alignment = BoxContainer.ALIGNMENT_BEGIN
		for serv_uuid in Globals.server_list:
			var serv = Globals.server_list[serv_uuid]
			var serv_item = server_item_scene.instantiate()
			serv_item.setup(
				serv.get("server-name", ""),
				serv.get("mark", ""),
				serv["addr"],
				serv_item.CANT_CONNECT,
				serv_uuid
				)
			serv_item.selected.connect(select_server)
			serv_item.doubleclick.connect(change_server)
			$content/server_list/panel/maegin/scroll/server_list.add_child(serv_item)


func select_server(uuid: String):
	for child in $content/server_list/panel/maegin/scroll/server_list.get_children():
		if child.uuid == uuid:
			child.is_selected = true
		else:
			child.is_selected = false
		child._apply_theme()
	selected_server = uuid
	print("uuid %s" % uuid)


func change_server(uuid: String):
	$server_settings/settings/vbox/label.text = tr("SERVER_SELECTION_CHANGE_SEVER_TITLE")
	$server_settings/settings/vbox/actions/ok.text = tr("SERVER_SELECTION_SAVE_BUTTON")
	
	$server_settings/settings/vbox/mark/edit.text = Globals.server_list[uuid].get("mark", "")
	$server_settings/settings/vbox/addr/edit.text = Globals.server_list[uuid].get("addr", "")
	$server_settings/settings/vbox/login/edit.text = Globals.server_list[uuid].get("login", "")
	$server_settings/settings/vbox/password/edit.text = Globals.server_list[uuid].get("password", "")
	
	EXUtils.disconnect_all_pressed($server_settings/settings/vbox/actions/ok)
	$server_settings/settings/vbox/actions/ok.pressed.connect(_save_server_settings)
	$server_settings.show()


func _save_server_settings():
	Globals.server_list[selected_server]["mark"] = $server_settings/settings/vbox/mark/edit.text
	Globals.server_list[selected_server]["addr"] = $server_settings/settings/vbox/addr/edit.text
	Globals.server_list[selected_server]["login"] = $server_settings/settings/vbox/login/edit.text
	Globals.server_list[selected_server]["password"] = $server_settings/settings/vbox/password/edit.text
	Globals._save_config()
	_render_server_list()
	_close_settings_subwindow()


func _on_add_server_pressed() -> void:
	$server_settings/settings/vbox/label.text = tr("SERVER_SELECTION_ADD_SERVER_TITLE")
	$server_settings/settings/vbox/actions/ok.text = tr("SERVER_SELECTION_SAVE_BUTTON")
	EXUtils.disconnect_all_pressed($server_settings/settings/vbox/actions/ok)
	$server_settings/settings/vbox/actions/ok.pressed.connect(_add_new_server)
	$server_settings.show()


func _add_new_server():
	var uuid: String = uuid4.v4()
	var new_server: Dictionary = {
		"mark": $server_settings/settings/vbox/mark/edit.text,
		"addr": $server_settings/settings/vbox/addr/edit.text,
		"login": $server_settings/settings/vbox/login/edit.text,
		"password": $server_settings/settings/vbox/password/edit.text
	}
	
	Globals.server_list[uuid] = new_server
	Globals._save_config()
	_render_server_list()
	_close_settings_subwindow()


func _close_settings_subwindow():
	$server_settings.hide()
	$server_settings/settings/vbox/mark/edit.text = ""
	$server_settings/settings/vbox/addr/edit.text = ""
	$server_settings/settings/vbox/login/edit.text = ""
	$server_settings/settings/vbox/password/edit.text = ""


func _render_server_settings_subwin():
	$server_settings/settings/vbox/mark/label.text = tr("SERVER_SELECTION_MARK") + ": "
	$server_settings/settings/vbox/addr/label.text = tr("SERVER_SELECTION_ADDR") + ": "
	$server_settings/settings/vbox/login/label.text = tr("SERVER_SELECTION_LOGIN") + ": "
	$server_settings/settings/vbox/password/label.text = tr("SERVER_SELECTION_PASSWORD") + ": "
	$server_settings/settings/vbox/actions/cancel.text = tr("SERVER_SELECTION_CANCEL_BUTTON")


func _render_server_deletion_subwin():
	$server_delete_confirm/margin/content/actions/Ok.text = tr("SERVER_SELECTION_SERVER_DELETE_OK")
	$server_delete_confirm/margin/content/actions/Cancel.text = tr("SERVER_SELECTION_CANCEL_BUTTON")


func _delete_selected_server():
	Globals.server_list.erase(selected_server)
	_render_server_list()
	$server_delete_confirm.hide()


func _on_exit_pressed() -> void:
	get_tree().quit()


func _on_delete_server_pressed() -> void:
	if not selected_server:
		return
	var serv_name: String = ""
	if Globals.server_list[selected_server].get("mark"):
		serv_name = Globals.server_list[selected_server].get("mark")
	elif Globals.server_list[selected_server].get("server-name"):
		serv_name = Globals.server_list[selected_server].get("server-name")
	elif Globals.server_list[selected_server].get("addr"):
		serv_name = Globals.server_list[selected_server].get("addr")
	else:
		serv_name = "Undefined server"
	$server_delete_confirm/margin/content/label.text = tr("SERVER_SELECTION_SERVER_DELETE_MSG") + " " + serv_name
	$server_delete_confirm.show()


func _on_settings_pressed():
	var settings_view_instance = settings_view.instantiate()
	get_tree().root.add_child(settings_view_instance)
	queue_free()
