extends Control

var image: Image
var parent: Node


# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	parent = get_node("/root/library")



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _on_select_file_pressed():
	$FileDialog.show()


func _on_create_system_pressed():
	if not image:
		image = Image.load_from_file("res://assets/placeholder.png")
	var image_name = await ResLoader.put_image(image)
	if not image_name: return
	var creation_result = await ResLoader.create_system($vbox/game_system_name.text, $vbox/game_system_codename.text, image_name)
	if not creation_result: return
	parent.remove_tab_by_ref(self)


func _on_file_dialog_file_selected(path):
	$vbox/file_chose/label.text = path
	image = Image.load_from_file(path)
	$vbox/refrect/texture.texture = ImageTexture.create_from_image(image)
