extends VBoxContainer

@onready var row_scene = preload("res://scenes/additional/library_additional/note_creation_add/list_row_item.tscn")



func get_rows_content():
	var content: Array = []
	for child in $rows.get_children():
		if not child.get_meta("deleted", false):
			content.append(child.get_content())
	return content


func redraw():
	var content: Array = []
	for child in $rows.get_children():
		if not child.get_meta("deleted", false):
			content.append(child.get_content())
		child.queue_free()
	
	for index in content.size():
		var row_instance = row_scene.instantiate()
		row_instance.deleted.connect(_delete_row.bind(row_instance))
		row_instance.set_content(content[index])
		row_instance.set_row_index(index + 1)
		$rows.add_child(row_instance)


func add_row(row_data: String, with_redraw: bool = true):
	var row_instance = row_scene.instantiate()
	row_instance.set_content(row_data)
	$rows.add_child(row_instance)
	if with_redraw:
		redraw()


func add_rows(rows_data: Array):
	for row_data in rows_data:
		add_row(row_data, false)
	redraw()


func _on_add_pressed():
	var row_instance = row_scene.instantiate()
	$rows.add_child(row_instance)
	redraw()


func _delete_row(instance: HBoxContainer):
	instance.set_meta("deleted", true)
	redraw()
