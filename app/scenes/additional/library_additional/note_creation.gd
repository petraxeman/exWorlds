extends Control

@onready var image_selector_scene = preload("res://scenes/additional/library_additional/note_creation_add/select_image.tscn")
@onready var tab_container_scene = preload("res://scenes/additional/library_additional/create_table/tab_container.tscn")
@onready var gelery_scene = preload("res://scenes/additional/library_additional/note_creation_add/gelery.tscn")
@onready var list_scene = preload("res://scenes/additional/library_additional/note_creation_add/list.tscn")

var table_name: String:
	set(value):
		$margin/scroll/vbox/info/Label.text = "Create note in \"%s\"" % value
var game_system: String
var table_codename: String

var note_data: Dictionary = {}
var table_nodes: Dictionary = {}
var codenames_map: Dictionary = {}
var note_table: Array = []



func render_table():
	table_nodes = {}
	for row in note_table:
		parse_row($margin/scroll/vbox/content, row)


func parse_row(container, row_data: Array):
	var row_box: HBoxContainer = HBoxContainer.new()
	
	for element in row_data:
		if not element["type"] in ["block", "tab_container"]:
			codenames_map[element["codename"]] = element
		
		match element["type"]:
			"string":
				var base: BoxContainer = build_field_base(element.get("name", ""))
				if element.get("as_type", "") != "":
					var entry: OptionButton = OptionButton.new()
					var items: Array = element.get("as_type", "").split(";")
					for item in items:
						if item.strip_edges(true, true) == "":
							continue
						entry.add_item(item.strip_edges(true, true))
					entry.text = note_data.get(element["codename"], {}).get("value", "")
					base.add_child(entry)
				else:
					var entry: LineEdit = LineEdit.new()
					entry.size_flags_horizontal = Control.SIZE_EXPAND_FILL
					entry.size_flags_vertical = Control.SIZE_SHRINK_CENTER
					entry.placeholder_text = element.get("placeholder", "")
					table_nodes[element["codename"]] = entry
					entry.text = note_data.get(element["codename"], {}).get("value", "")
					base.add_child(entry)
				row_box.add_child(base)
			"paragraph":
				var base: VBoxContainer = build_field_base(element.get("name", ""))
				var text_edit = TextEdit.new()
				text_edit.scroll_fit_content_height = true
				text_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				text_edit.text = note_data.get(element["codename"], {}).get("value", "")
				table_nodes[element["codename"]] = text_edit
				base.add_child(text_edit)
				row_box.add_child(base)
			"number":
				var base: VBoxContainer = build_field_base(element.get("name", ""))
				var entry
				if element.get("subtype", "integer") == "dice":
					entry = LineEdit.new()
					entry.size_flags_horizontal = Control.SIZE_EXPAND_FILL
					entry.size_flags_vertical = Control.SIZE_SHRINK_CENTER
					entry.placeholder_text = "XdZZ"
					entry.text = note_data.get(element["codename"], {}).get("value", "")
				else:
					entry = SpinBox.new()
					entry.min_value = float(element.get("min", "0"))
					entry.max_value = float(element.get("max", "100"))
					if element.get("subtype", "integer") == "float":
						entry.step = 0.01
						entry.value = float(note_data.get(element["codename"], {}).get("value", 0))
					else:
						entry.value = int(note_data.get(element["codename"], {}).get("value", 0))
				table_nodes[element["codename"]] = entry
				base.add_child(entry)
				row_box.add_child(base)
			"bool":
				var base: HBoxContainer = build_field_base(element.get("name", ""), "horizontal")
				var check_button: CheckButton = CheckButton.new()
				var toggle_mode = note_data.get(element["codename"], {}).get("value", false) 
				if str(toggle_mode) == "true":
					check_button.button_pressed = true
				base.add_child(check_button)
				row_box.add_child(base)
			"list":
				var base: VBoxContainer = build_field_base(element.get("name", ""))
				var list: VBoxContainer = list_scene.instantiate()
				var rows: Array = note_data.get(element["codename"], {}).get("value", [])
				list.ready.connect(func(): list.add_rows(rows))
				table_nodes[element["codename"]] = list
				base.add_child(list)
				row_box.add_child(base)
			"table":
				pass
			"block":
				var block_box: VBoxContainer = VBoxContainer.new()
				block_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				var block_label: Label = Label.new()
				block_label.text = element["name"]
				block_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				block_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
				block_box.add_child(block_label)
				for row in element["rows"]:
					parse_row(block_box, row)
				row_box.add_child(block_box)
			"tab_container":
				var tab_container: VBoxContainer = tab_container_scene.instantiate()
				tab_container.can_be_changed = false
				for tab in element['tabs']:
					var page: VBoxContainer = tab_container.add_page(tab["name"])
					for row in tab["rows"]:
						parse_row(page, row)
				row_box.add_child(tab_container)
			"image":
				var base: VBoxContainer = build_field_base(element.get("name", ""))
				base.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
				var image_selector: TextureRect = image_selector_scene.instantiate()
				table_nodes[element["codename"]] = image_selector
				var image_name: String = note_data.get(element["codename"], {}).get("value", "")
				if image_name != "":
					var image: Dictionary = await ResLoader.get_image(image_name)
					image_selector.image = image["image"]
					image_selector.texture = ImageTexture.create_from_image(image["image"])
					image_selector.image_name = image_name
				base.add_child(image_selector)
				row_box.add_child(base)
			"gelery":
				var base: VBoxContainer = build_field_base(element.get("name", ""))
				base.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				var gelery_instance = gelery_scene.instantiate()
				for image_name in note_data.get(element["codename"], {}).get("value", []):
					var image: Dictionary = await ResLoader.get_image(image_name)
					gelery_instance.add_image(image_name, image["image"])
				gelery_instance.ready.connect(func(): gelery_instance.render())
				table_nodes[element["codename"]] = gelery_instance
				base.add_child(gelery_instance)
				row_box.add_child(base)
	container.add_child(row_box)


func build_field_base(field_name: String, alignment: String = "vertical") -> BoxContainer:
	var container: BoxContainer
	match alignment:
		"horizontal":
			container = HBoxContainer.new()
		"vertical":
			container = VBoxContainer.new()
	
	container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	container.alignment = BoxContainer.ALIGNMENT_CENTER
	if field_name != "":
		var label: Label = Label.new()
		label.text = field_name + ":"
		container.add_child(label)
	return container


func build_note_data() -> Dictionary:
	var prep_note_data: Dictionary = {}
	for codename in table_nodes:
		var field_data: Dictionary = codenames_map[codename]
		match field_data["type"]:
			"number":
				match field_data.get("subtype", "integer"):
					"integer":
						prep_note_data[codename] = {"type": "number", "value": table_nodes[codename].value}
					"float":
						prep_note_data[codename] = {"type": "number", "value": table_nodes[codename].value}
					"dice":
						prep_note_data[codename] = {"type": "number", "value": table_nodes[codename].text}
			"string":
				prep_note_data[codename] = {"type": "string", "value": table_nodes[codename].text}
			"bool":
				prep_note_data[codename] = {"type": "bool", "value": table_nodes[codename].button_pressed}
			"paragraph":
				prep_note_data[codename] = {"type": "paragraph", "value": table_nodes[codename].text}
			"list":
				prep_note_data[codename] = {"type": "list", "value": table_nodes[codename].get_rows_content()}
			"image":
				prep_note_data[codename] = {"type": "image", "value": table_nodes[codename].image_name}
			"gelery":
				prep_note_data[codename] = {"type": "gelery", "value": table_nodes[codename].get_images().keys()}
	return prep_note_data


func upload_parts(prep_note_data: Dictionary):
	for codename in prep_note_data:
		match prep_note_data[codename]["type"]:
			"image":
				if prep_note_data[codename]["value"] != "":
					continue
				var image_name: String = await ResLoader.put_image(table_nodes[codename].get_image())
				prep_note_data[codename]["value"] = image_name
			"gelery":
				var images: Dictionary = table_nodes[codename].get_images()
				var new_images: Array = []
				for temp_name in images.keys():
					var name_and_ext: Array = temp_name.split(".")
					if name_and_ext[1] == "new":
						var image_name: String = await ResLoader.put_image(images[temp_name])
						new_images.append(image_name)
					else:
						new_images.append(temp_name)
				prep_note_data[codename]["value"] = new_images
	return prep_note_data


func validate_note(prep_note_data: Dictionary) -> bool:
	var codename_field_exists: bool = false
	for codename in prep_note_data:
		if codename == "codename" and prep_note_data[codename].get("value", "") != "":
			codename_field_exists = true
	if not codename_field_exists:
		return false
	return true

func _on_create_pressed():
	var prepared_note_data: Dictionary = build_note_data()
	if not validate_note(prepared_note_data):
		return
	await upload_parts(prepared_note_data)
	await ResLoader.send_note(game_system, table_codename, prepared_note_data)
	get_node("/root/library").remove_tab_by_ref(self)
