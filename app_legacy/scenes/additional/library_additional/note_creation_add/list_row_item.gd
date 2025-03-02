extends HBoxContainer

signal deleted



func get_content() -> String:
	return $text_edit.text


func set_content(text: String) -> void:
	$text_edit.text = text


func set_row_index(index: int) -> void:
	$label.text = "Row %s:" % str(index)


func _on_del_pressed():
	emit_signal("deleted")
