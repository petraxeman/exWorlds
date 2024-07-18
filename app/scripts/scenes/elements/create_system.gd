extends Control

var image: Image

func _ready():
	pass


func _on_select_file_pressed():
	$FileDialog.show()


func _on_create_system_pressed():
	if not image:
		image = Image.load_from_file("res://assets/placeholder.png")
	var image_name = await ResLoader.put_image(image)
	ResLoader.create_system($vbox/game_system_name.text, $vbox/game_system_code_name.text, image_name)
	var tab_container: TabContainer = self.get_parent()
	var tab_bar: TabBar = self.get_parent().get_parent().get_node("tab_bar")
	var index = tab_container.get_children().find(self)
	tab_bar.remove_tab(index)
	self.queue_free()


func _on_file_dialog_file_selected(path):
	$vbox/file_chose/label.text = path
	image = Image.load_from_file(path)
	$vbox/refrect/texture.texture = ImageTexture.create_from_image(image)
