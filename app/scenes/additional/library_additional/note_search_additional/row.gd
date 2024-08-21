extends PanelContainer

signal open_note(note_codename: String)

var note_codename: String


func build(codename: String, data: Array):
	note_codename = codename
	for child in $margin/hbox.get_children():
		child.queue_free()
	
	for element in data:
		if not (element is String) and element.get("image"):
			var image_texture: TextureRect = TextureRect.new()
			image_texture.texture = ImageTexture.create_from_image(element.get("image"))
			image_texture.custom_minimum_size = Vector2(50, 50)
			image_texture.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
			image_texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			image_texture.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			$margin/hbox.add_child(image_texture)
		elif element is String:
			var label: Label = Label.new()
			label.text = element if element else " "
			label.clip_text = true
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			$margin/hbox.add_child(label)
		else:
			var label: Label = Label.new()
			label.text = element if element else " "
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			$margin/hbox.add_child(label)


func _on_gui_input(event):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and not event.pressed:
			emit_signal("open_note", note_codename)
