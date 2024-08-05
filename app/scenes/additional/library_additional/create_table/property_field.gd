extends HBoxContainer



func get_data() -> Array:
	return [$codename.text, $value.text]


func _on_del_pressed():
	queue_free()
