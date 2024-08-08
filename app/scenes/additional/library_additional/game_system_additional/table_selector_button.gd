extends MarginContainer

signal button_pressed

var table_codename: String
var game_system: String
var game_system_view
@onready var library: Node = get_node("/root/library")



func _input(event):
	var lower_border = self.global_position
	var upper_border = self.global_position + self.size
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and \
		(event.position.x > lower_border.x) and (event.position.y > lower_border.y) and \
		(event.position.x < upper_border.x) and (event.position.y < upper_border.y):
		emit_signal("button_pressed")


func set_icon(icon_name: String):
	$panel/margin/hbox/icon.texture = Icons.get_icon(icon_name)


func set_texture(texture: ImageTexture):
	$panel/margin/hbox/icon.texture = texture


func set_label(text: String):
	$panel/margin/hbox/name.text = text
	$ConfirmationDialog.dialog_text = "Are you sure you want to delete table \"%s\"?" % text


func _on_confirmation_dialog_confirmed():
	var result: bool = await ResLoader.delete_table(game_system, table_codename)
	if result:
		game_system_view.render_categories()


func _on_delete_pressed():
	$ConfirmationDialog.show()


func _on_settings_pressed():
	var result = await ResLoader.get_table(game_system, table_codename)
	if result.get("Ok", false):
		var create_table_view = library.create_tab("create_table")
		create_table_view.table = result["table"]
		create_table_view.apply_common(result["common"])
		create_table_view.apply_macros(result["macros"])
		create_table_view.apply_properties(result["properties"])
		create_table_view.disable_codename_field()
		create_table_view.render_table()
