extends Control

@onready var froot = $margin/vbox/scroll/vbox/main_view/vbox

@onready var hadd_field = preload("res://scenes/additional/library_additional/create_table/horizontal_add_field_button.tscn")
@onready var vadd_field = preload("res://scenes/additional/library_additional/create_table/vertical_add_field_button.tscn")
@onready var field_scene = preload("res://scenes/additional/library_additional/create_table/field.tscn")
@onready var tab_scene = preload("res://scenes/additional/library_additional/create_table/tab_container.tscn")
@onready var block_scene = preload("res://scenes/additional/library_additional/create_table/block.tscn")
@onready var macro_field = preload("res://scenes/additional/library_additional/create_table/macro_field.tscn")
@onready var property_field = preload("res://scenes/additional/library_additional/create_table/property_field.tscn")

var types_map = {
	1: {"data": {"type": "string", "codename": "undefined", "name": ""}},
	2: {"data": {"type": "paragraph", "codename": "undefined", "name": ""}},
	3: {"data": {"type": "number", "codename": "undefined", "name": ""}},
	4: {"data": {"type": "bool", "codename": "undefined", "name": ""}},
	5: {"data": {"type": "list", "codename": "undefined", "name": ""}},
	6: {"data": {"type": "image", "codename": "undefined", "name": ""}},
	7: {"data": {"type": "gelery", "codename": "undefined", "name": ""}},
	8: {"data": {"type": "macro", "codename": "undefined", "name": ""}},	
	10: {"data": {"type": "block", "name": "Common", "rows": []}},
	11: {"data": {"type": "tab", "tabs": []}},
}

var type_to_field = {
	"default": {
		"codename": {"type": "LineEdit", "name": "Codename:", "placeholder": "field-codename"},
		"name": {"type": "LineEdit", "name": "Name:", "placeholder": "Name of field"},
		"default": {"type": "LineEdit", "name": "Default:", "placeholder": "Default value"},
		"placeholder": {"type": "LineEdit", "name": "Placeholder:", "placeholder": "This text"},
		"hide_if_empty": {"type": "CheckButton", "name": "Hide if empty:"},
		"hide_name": {"type": "CheckButton", "name": "Hide name:"},
		"hide": {"type": "CheckButton", "name": "Hide field:"}
	},
	"string": {
		"size": {"type": "SpinBox", "name": "Size of text:", "min": 0, "max": 5, "value": 0},
		"as_type": {"type": "LineEdit", "name": "As type:", "placeholder": "Value1; Value2; Value3"}
	},
	"paragraph": {},
	"number": {
		"subtype": {"type": "OptionButton", "name": "Subtype:", "text": "integer", "variants": ["integer", "float", "dice"]}
	},
	"bool": {},
	"list": {
		"group_by": {"type": "LineEdit", "name": "Group by:", "placeholder": "field name"},
		"possible_types": {"type": "LineEdit", "name": "Possible tables:", "placeholder": "@table1; @table2; @table3"},
	},
	"image": {},
	"gelery": {
		"max_images": {"type": "SpinBox", "name": "Max images:", "min": 0, "max": 100, "value": 0},
		"images_per_page": {"type": "SpinBox", "name": "Images per page:", "min": 0, "max": 100, "value": 0},
	}
}

var settings_map = {}

var add_field_container = []
var add_field_index: int = -1
var add_field_new_line: bool = false
var field_setup_source: Dictionary = {}

var table: Array = []



func _ready():
	render_table()


func render_table():
	for child in froot.get_children():
		child.queue_free()
	
	table.erase([])
	
	var add_zero = hadd_field.instantiate()
	add_zero.pressed.connect(_add_field_at.bind(table, 0, true))
	froot.add_child(add_zero)
	for row_index in range(table.size()):
		var row = table[row_index]
		var row_box: HBoxContainer = HBoxContainer.new()
		parse_data(row_box, table[row_index])
		froot.add_child(row_box)
		
		var add_button = hadd_field.instantiate()
		add_button.pressed.connect(_add_field_at.bind(table, row_index + 1, true))
		froot.add_child(add_button)


func parse_data(container: Node, data: Array):
	if container is HBoxContainer:
		var add_field = vadd_field.instantiate()
		add_field.pressed.connect(_add_field_at.bind(data, 0))
		container.add_child(add_field)
	else:
		var add_field = hadd_field.instantiate()
		add_field.pressed.connect(_add_field_at.bind(data, 0))
		container.add_child(add_field)
	
	for index in range(data.size()):
		if data[index]["type"] == "block":
			var block_box: VBoxContainer = block_scene.instantiate()
			block_box.set_block_name(data[index]["name"])
			block_box.delete_block.connect(_on_delete_field_pressed.bind(data, data[index]))
			
			var add_field = hadd_field.instantiate()
			add_field.pressed.connect(_add_field_at.bind(data[index]["rows"], 0, true))
			block_box.add_child(add_field)
			
			for row_block_index in range(data[index]["rows"].size()):
				var row_box: HBoxContainer = HBoxContainer.new()
				row_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				parse_data(row_box, data[index]["rows"][row_block_index])
				block_box.add_child(row_box)
				
				var add_field_after = hadd_field.instantiate()
				add_field_after.pressed.connect(_add_field_at.bind(data[index]["rows"], row_block_index + 1, true))
				block_box.add_child(add_field_after)
			
			container.add_child(block_box)
		elif data[index]["type"] == "tab":
			var new_tabs: VBoxContainer = tab_scene.instantiate()
			new_tabs.delete_tab.connect(_on_delete_field_pressed.bind(data, data[index]))
			for tab in data[index]["tabs"]:
				var page_vbox: VBoxContainer = new_tabs.add_page(tab["name"])
				parse_data(page_vbox, tab["rows"])
			container.add_child(new_tabs)
		else:
			var new_field: PanelContainer = field_scene.instantiate()
			var field_data: Dictionary = data[index]
			new_field.set_data(field_data.get("type", "Undefined"), field_data.get("codename", ""), field_data.get("name", ""))
			new_field.change_field.connect(_on_settings_field_pressed.bind(field_data))
			new_field.delete_field.connect(_on_delete_field_pressed.bind(data, field_data))
			container.add_child(new_field)
		
		if container is HBoxContainer:
			var add_field = vadd_field.instantiate()
			add_field.pressed.connect(_add_field_at.bind(data, index + 1))
			container.add_child(add_field)
		else:
			var add_field = hadd_field.instantiate()
			add_field.pressed.connect(_add_field_at.bind(data, index + 1))
			container.add_child(add_field)


func render_field_setup():
	for key in settings_map:
		settings_map.erase(key)
	
	for child in $field_setup.get_children():
		child.queue_free()
	
	var root_vbox: VBoxContainer = VBoxContainer.new()
	root_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	
	var settings: Dictionary = {}
	#if field_setup_source["type"] in ["paragraph", "string", "number", "list"]:
	settings.merge(type_to_field["default"])
	settings.merge(type_to_field[field_setup_source["type"]], true)
	
	for parametr_key: String in settings:
		var parametr: Dictionary = settings[parametr_key]
		var row: HBoxContainer = HBoxContainer.new()
		var parametr_label: Label = Label.new()
		parametr_label.text = parametr.get("name", "") + "  "
		row.add_child(parametr_label)
			
		if parametr["type"] == "LineEdit":
			var lineedit: LineEdit = LineEdit.new()
			lineedit.placeholder_text = parametr.get("placeholder", "")
			lineedit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			lineedit.text = field_setup_source.get(parametr_key, "")
			settings_map[parametr_key] = lineedit
			row.add_child(lineedit)
		elif parametr["type"] == "CheckButton":
			var checkbutton: CheckButton = CheckButton.new()
			checkbutton.button_pressed = field_setup_source.get(parametr_key, false)
			settings_map[parametr_key] = checkbutton
			row.add_child(checkbutton)
		elif parametr["type"] == "SpinBox":
			var spinbox: SpinBox = SpinBox.new()
			spinbox.min_value = parametr.get("min", 0)
			spinbox.max_value = parametr.get("max", 100)
			spinbox.value = field_setup_source.get(parametr_key, 0)
			settings_map[parametr_key] = spinbox
			row.add_child(spinbox)
		elif parametr["type"] == "OptionButton":
			var optionbutton: OptionButton = OptionButton.new()
			for variant in parametr["variants"]:
				optionbutton.add_item(variant)
			optionbutton.text = field_setup_source.get(parametr_key, "") if field_setup_source.get(parametr_key, false) else parametr.get("text", "")
			optionbutton.get_popup().always_on_top = true
			settings_map[parametr_key] = optionbutton
			row.add_child(optionbutton)
		root_vbox.add_child(row)
	var submit_button: Button = Button.new()
	submit_button.text = "Submit"
	submit_button.pressed.connect(_on_field_setup_submited)
	root_vbox.add_child(submit_button)
	$field_setup.add_child(root_vbox)


func create_field(index: int) -> void:
	var new_field = types_map[index]["data"].duplicate()
	if add_field_new_line:
		add_field_container.insert(add_field_index, [new_field])
	else:
		add_field_container.insert(add_field_index, new_field)
	render_table()


func _on_field_type_selected(index: int):
	if index == 13:
		$field_type_selector.hide()
		return
	create_field(index)


func _on_add_new_field_pressed():
	$field_type_selector.show()


func _on_save_and_upload_pressed():
	for child in $margin/vbox/scroll/vbox/main_view/vbox.get_children():
		var data: Dictionary = child.get_data()
		if data["Ok"]:
			data.erase("Ok")
			print(data)


func _on_settings_field_pressed(source):
	if source is Dictionary:
		field_setup_source = source
		render_field_setup()
		$field_setup.show()


func _on_field_setup_submited():
	var new_settings: Dictionary = {}
	var settings: Dictionary = {}
	
	#if field_setup_source["type"] in ["paragraph", "string", "number", "list"]:
	settings.merge(type_to_field["default"])
	settings.merge(type_to_field[field_setup_source["type"]])
	
	for parametr_key: String in settings:
		var parametr: Dictionary = settings[parametr_key]
		if parametr["type"] in ["LineEdit", "OptionButton"]:
			field_setup_source[parametr_key] = settings_map[parametr_key].text
		elif parametr["type"] == "SpinBox":
			field_setup_source[parametr_key] = settings_map[parametr_key].value
		elif parametr["type"] in ["CheckButton", "CheckBox"]:
			field_setup_source[parametr_key] = settings_map[parametr_key].button_pressed
	
	render_table()
	field_setup_source = {}
	$field_setup.hide()


func _on_delete_field_pressed(container: Array, data: Dictionary):
	container.erase(data)
	render_table()


func _add_field_at(container: Array, index: int, new_line: bool = false):
	add_field_container = container
	add_field_index = index
	add_field_new_line = new_line
	$field_type_selector.show()


func _on_add_macro_pressed():
	var new_macro: HBoxContainer = macro_field.instantiate()
	$margin/vbox/scroll/vbox/macros/elements/vbox.add_child(new_macro)


func _on_add_property_pressed():
	var new_property: HBoxContainer = property_field.instantiate()
	$margin/vbox/scroll/vbox/properties/elements/vbox.add_child(new_property)
