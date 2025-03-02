extends MarginContainer

signal button_pressed

var table_codename: String
var game_system: String
var game_system_view

@onready var library: Node = get_node("/root/library")



func set_icon(icon_name: String):
	$panel/margin/hbox/icon.texture = ImageTexture.create_from_image(Icons.get_icon(icon_name))


func set_texture(texture: ImageTexture):
	$panel/margin/hbox/icon.texture = texture


func set_label(text: String):
	$panel/margin/hbox/name.text = text
	$ConfirmationDialog.dialog_text = "Are you sure you want to delete table \"%s\"?" % text


func disable_changment():
	$panel/margin/hbox/settings.hide()
	$panel/margin/hbox/delete.hide()


func _on_confirmation_dialog_confirmed():
	var result: bool = await ResLoader.delete_table(game_system, table_codename)
	if result:
		game_system_view.render_categories()


func _on_delete_pressed():
	$ConfirmationDialog.show()


func _on_settings_pressed():
	var result = await ResLoader.get_table(game_system, table_codename)
	if not result.get("Ok", false):
		return
	result = result["table_data"]
	var create_table_view = library.create_tab("create_table")
	create_table_view.game_system = game_system
	create_table_view.table = result["table"]
	create_table_view.apply_common(result["common"])
	create_table_view.apply_macros(result["macros"])
	create_table_view.apply_properties(result["properties"])
	create_table_view.disable_codename_field()
	create_table_view.render_table()


func _on_create_new_pressed():
	var result = await ResLoader.get_table(game_system, table_codename)
	if not result.get("Ok", false):
		return
	result = result["table_data"]
	var note_creation = library.create_tab("create_note")
	note_creation.table_name = result["common"]["table_name"]
	note_creation.game_system = game_system
	note_creation.table_codename = table_codename
	note_creation.note_table = result["table"]
	note_creation.render_table()


func _on_panel_gui_input(event):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and not event.pressed:
			emit_signal("button_pressed")
			_on_table_selected()


func _on_table_selected():
	var note_viewer = library.create_tab("note_viewer")
	note_viewer.setup(game_system, table_codename)
