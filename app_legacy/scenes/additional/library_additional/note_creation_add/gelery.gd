extends PanelContainer

var images: Dictionary = {}
var max_images: int = 25

@onready var image_scene = preload("res://scenes/additional/library_additional/note_creation_add/gelery_image_item.tscn")


func render():
	for child in $margin/scroll/vbox.get_children():
		child.queue_free()
	
	var first_row: HBoxContainer = HBoxContainer.new()
	first_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	first_row.add_theme_constant_override("separation", 10)
	var second_row: HBoxContainer = HBoxContainer.new()
	second_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	second_row.add_theme_constant_override("separation", 10)
	
	var line: int = 1
	for image_name in images:
		var image_inst = image_scene.instantiate()
		image_inst.set_image(image_name, images[image_name])
		image_inst.delete.connect(delete_image.bind(image_name))
		image_inst.show_image.connect(show_image.bind(image_name))
		
		if line == 1:
			first_row.add_child(image_inst)
		else:
			second_row.add_child(image_inst)
		line *= -1
	
	if images.keys().size() < max_images:
		var add_new = image_scene.instantiate()
		add_new.can_be_changed = false
		add_new.show_image.connect(_on_add_new_pressed)
		if line == 1:
			first_row.add_child(add_new)
		else:
			second_row.add_child(add_new)
	$margin/scroll/vbox.add_child(first_row)
	$margin/scroll/vbox.add_child(second_row)


func delete_image(image_name: String):
	images.erase(image_name)
	render()


func show_image(_image_name: String):
	pass


func add_image(image_name: String, image_data: Image):
	images[image_name] = image_data


func get_images() -> Dictionary:
	return images.duplicate(true)


func _on_add_new_pressed():
	$FileDialog.show()


func _on_file_dialog_file_selected(path):
	var new_image: Image = Image.load_from_file(path)
	var new_image_name: String = uuid4.v4() + ".new"
	images[new_image_name] = new_image
	render()
