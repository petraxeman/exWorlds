extends Control

var fields = {
	0: ["String", preload("res://scenes/additional/library_additional/create_table_fields/string_field.tscn")],
	1: ["Paragraph", preload("res://scenes/additional/library_additional/create_table_fields/paragraph_field.tscn")],
	2: ["Number", preload("res://scenes/additional/library_additional/create_table_fields/number_field.tscn")],
	3: ["Bool", preload("res://scenes/additional/library_additional/create_table_fields/bool_field.tscn")],
	4: ["List", preload("res://scenes/additional/library_additional/create_table_fields/list_field.tscn")],
	5: ["Table", preload("res://scenes/additional/library_additional/create_table_fields/table_field.tscn")],
	6: ["Image", preload("res://scenes/additional/library_additional/create_table_fields/image_field.tscn")],
	7: ["Gelery", preload("res://scenes/additional/library_additional/create_table_fields/gelery_field.tscn")]
}


func create_field(index: int) -> void:
	var new_field: Node = fields[index][1].instantiate()
	new_field.parent = self
	$margin/vbox/scroll/vbox/main_view.add_child(new_field)


func _on_field_type_selected(index: int):
	create_field(index)


func _on_add_new_field_pressed():
	$field_type_selector.show()
