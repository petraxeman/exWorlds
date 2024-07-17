extends Control

var image: Image

func _ready():
	pass


func _on_select_file_pressed():
	$FileDialog.show()


func _on_create_system_pressed():
	if not image:
		image = Image.load_from_file("res://assets/Age_of_Ashes_1_-_Hellknight_Hill (1)-2.png")
	await ResLoader.put_image(image)
	return
	var tab_container: TabContainer = self.get_parent()
	var tab_bar: TabBar = self.get_parent().get_parent().get_node("tab_bar")
	var index = tab_container.get_children().find(self)
	tab_bar.remove_tab(index)
	self.queue_free()


func _on_file_dialog_file_selected(path):
	$vbox/file_chose/label.text = path
	image = Image.load_from_file(path)
	$vbox/refrect/texture.texture = ImageTexture.create_from_image(image)
