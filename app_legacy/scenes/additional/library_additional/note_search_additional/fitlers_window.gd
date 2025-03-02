extends Popup

signal filters_applied

var nodes_map: Dictionary = {}
var filter_use: bool = false


func render_fields(fields: Array, fields_map: Dictionary):
	nodes_map = {}
	for field in fields:
		var row: HBoxContainer = HBoxContainer.new()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		match fields_map.get(field, {}).get("type", "undefuned"):
			"string":
				var entry
				if fields_map.get(field).get("as_type", []) != []:
					entry = OptionButton.new()
					entry.get_popup().always_on_top = true
					for option in fields_map.get(field).get("as_type"):
						entry.add_item(option)
				else:
					entry = LineEdit.new()
					entry.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				
				if fields_map.get(field).get("name", "") != "":
					var label: Label = Label.new()
					label.text = fields_map.get(field).get("name") + ":"
					row.add_child(label)
				nodes_map[field] = {"type": "string", "node": entry}
				row.add_child(entry)
			"number":
				var from_spinbox: SpinBox = SpinBox.new()
				from_spinbox.max_value = 100000
				var to_spinbox: SpinBox = SpinBox.new()
				to_spinbox.max_value = 100000
				
				if fields_map.get(field).get("name", "") != "":
					var name_label: Label = Label.new()
					name_label.text = fields_map.get(field).get("name") + ":"
					row.add_child(name_label)
				var from_label: Label = Label.new()
				from_label.text = "from"
				var to_label: Label = Label.new()
				to_label.text = "to"
				var search_type: OptionButton = OptionButton.new()
				for check_type in ["min", "max", "avg"]:
					search_type.add_item(check_type)
				row.add_child(search_type)
				row.add_child(from_label)
				row.add_child(from_spinbox)
				row.add_child(to_label)
				row.add_child(to_spinbox)
				nodes_map[field] = {"type": "number", "search_type": search_type, "min": from_spinbox, "max": to_spinbox}
			"paragraph", "list":
				var line_edit = LineEdit.new()
				line_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				
				if fields_map.get(field).get("name", "") != "":
					var label: Label = Label.new()
					label.text = fields_map.get(field).get("name") + ":"
					row.add_child(label)
				
				nodes_map[field] = {"type": "string", "node": line_edit}
				row.add_child(line_edit)
			"bool":
				var check_button: CheckButton = CheckButton.new()
				if fields_map.get(field).get("name", "") != "":
					var label: Label = Label.new()
					label.text = fields_map.get(field).get("name") + ":"
					row.add_child(label)
				nodes_map[field] = {"type": "bool", "node": check_button}
				row.add_child(check_button)
		$margin/content/rows.add_child(row)


func get_filter():
	if not filter_use:
		return {}
	var filter: Dictionary = {}
	for codename in nodes_map:
		match nodes_map[codename]["type"]:
			"string":
				if nodes_map[codename]["node"].text == "":
					continue
				filter[codename] = {"value": nodes_map[codename]["node"].text}
			"number":
				if nodes_map[codename]["min"].value == 0 and nodes_map[codename]["max"].value == 0:
					continue
				var check_string = "check_avg_value"
				match nodes_map[codename]["search_type"].text:
					"min":
						check_string = "check_min_value"
					"max":
						check_string = "check_max_value"
					"avg":
						check_string = "check_avg_value"
				filter[codename] = {"min": nodes_map[codename]["min"].value, "max": nodes_map[codename]["max"].value, check_string: true}
			"bool":
				filter[codename] = {"value": nodes_map[codename]["node"].button_pressed}
	return filter


func _on_cancel_pressed():
	hide()


func _on_apply_pressed():
	filter_use = true
	emit_signal("filters_applied")
	hide()


func _on_discard_pressed():
	filter_use = false
	hide()

