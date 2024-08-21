extends Control

var note: Dictionary
var table: Dictionary
var note_addr: Dictionary



func setup(addr: Dictionary):
	note = await ResLoader.get_note(addr["game_system"], addr["table"], addr["note"])
	table = await ResLoader.get_table(addr["game_system"], addr["table"])
	note_addr = addr
	$content/note_name/hbox/label.text = "Note \"{0}\"".format([addr["note"]])
	render()


func render():
	var context: Dictionary = {}
	for row in table["table_data"]["table"]:
		parse_row(row, context)


func parse_row(row: Array, context: Dictionary):
	var row_box: HBoxContainer = HBoxContainer.new()
	row_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for field in row:
		if field.get("hide", false):
			continue
		
		var field_box: VBoxContainer = VBoxContainer.new()
		field_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		
		if not field.get("hide_name", false):
			var name_label: Label = Label.new()
			name_label.text = field.get("name", "") + ":"
			field_box.add_child(name_label)
		
		match field["type"]:
			"string":
				var text: String = note.get(field["codename"], {}).get("value", "")
				text = await TextLib.format(text, note_addr, context)
				
				if field.get("hide_if_empty", false) and text == "":
					continue
				
				if text == "":
					text = "-"
				var string_label: Label = create_string(text)
				field_box.add_child(string_label)
				row_box.add_child(field_box)
			"image":
				var image_box: VBoxContainer = VBoxContainer.new()
				image_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				
				var image_name: String = note.get(field["codename"], {}).get("value", "")
				var image: Dictionary = await ResLoader.get_image(image_name)
				var texture_rect: TextureRect = TextureRect.new()
				if not image.get("image", false):
					if field.get("hide_if_empty", false):
						continue
					image = {"image": Image.load_from_file("res://assets/placeholder.png")}
				texture_rect.texture = ImageTexture.create_from_image(image["image"])
				texture_rect.custom_minimum_size = Vector2(150, 150)
				texture_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
				texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				texture_rect.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				field_box.add_child(texture_rect)
				row_box.add_child(field_box)
			"paragraph":
				var text: String = note.get(field["codename"], {}).get("value", "")
				text = await TextLib.format(text, note_addr, context)
				
				if field.get("hide_if_empty", false) and text == "":
					continue
				
				if text == "":
					text = "-"
				var mdstring_label: MarkdownLabel = create_mdstring(text)
				field_box.add_child(mdstring_label)
				row_box.add_child(field_box)
			"bool":
				if not note.get(field["codename"], {}).get("value", false) and field.get("hide_if_empty", false):
					continue
				var text: String = "Yes" if note.get(field["codename"]).get("value", false) else "No"
				var string: Label = create_string(text)
				field_box.add_child(string)
				row_box.add_child(field_box)
			"number":
				var number_label: Label = Label.new()
				var number_data = note.get(field["codename"], {"min": 0, "max": 0, "avg": 0, "org": 0})
				number_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL 
				number_label.clip_text = true
				if number_data.get("min", 0) == 0 and number_data.get("max", 0) == 0 and field.get("hide_if_empty", false):
					continue
				if field.get("subtype", "integer") in ["integer", "float"]:
					number_label.text = str(number_data.get("org", 0))
				elif field.get("subtype", "integer") == "dice":
					number_label.text = "{0} ({1}-{2} / {3})".format([
						number_data.get("org", 0),
						number_data.get("min", 0),
						number_data.get("max", 0),
						number_data.get("avg", 0)
					])
				field_box.add_child(number_label)
				row_box.add_child(field_box)
			"list":
				pass
			"block":
				pass
			"tab_container":
				pass
		
	$content/scroll/margin/vbox.add_child(row_box)


func create_string(text: String) -> Label:
	var string: Label = Label.new()
	string.text = text
	string.size_flags_horizontal = Control.SIZE_EXPAND_FILL 
	string.clip_text = true
	return string


func create_mdstring(text: String) -> MarkdownLabel:
	var mdstring: MarkdownLabel = MarkdownLabel.new()
	mdstring.markdown_text = text
	mdstring.fit_content = true
	mdstring.size_flags_horizontal = Control.SIZE_EXPAND_FILL 
	return mdstring


func _on_edit_pressed():
	pass # Replace with function body.


func _on_delete_pressed():
	await ResLoader.delete_note(note_addr["game_system"], note_addr["table"], note_addr["note"])
	get_node("/root/library").remove_tab_by_ref(self)
	
