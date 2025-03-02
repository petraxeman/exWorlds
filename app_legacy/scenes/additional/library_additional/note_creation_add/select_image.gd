extends TextureRect

var image: Image
var image_name: String = ""

var mouse_in: bool = false


func get_image() -> Image:
	return image


func _on_mouse_entered():
	mouse_in = true


func _on_mouse_exited():
	mouse_in = false


func _on_gui_input(event):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed == false:
			$FileDialog.show()


func _on_file_dialog_file_selected(path: String):
	image = Image.load_from_file(path)
	texture = ImageTexture.create_from_image(image)
	image_name = ""
