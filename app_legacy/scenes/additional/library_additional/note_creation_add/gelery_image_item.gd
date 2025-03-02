extends TextureRect

signal show_image
signal delete

var mouse_in_button: bool = false
var image_name: String = ""

var can_be_changed: bool = true:
	set(value):
		if not value:
			$actions.hide()
		else:
			$actions.show()



func _on_gui_input(event):
	if event is InputEventMouseButton and not mouse_in_button:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed == false:
			emit_signal("show_image")


func set_image(iname: String, image: Image):
	texture = ImageTexture.create_from_image(image)
	image_name = iname


func _on_del_mouse_entered():
	mouse_in_button = true


func _on_del_mouse_exited():
	mouse_in_button = false


func _on_del_pressed():
	emit_signal("delete")
