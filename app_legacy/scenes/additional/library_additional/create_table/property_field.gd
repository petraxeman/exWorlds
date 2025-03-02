extends HBoxContainer



func set_data(codename: String, value: String):
	$codename.text = codename
	$value.text = value


func get_data() -> Array:
	return [$codename.text, $value.text]


func _on_del_pressed():
	queue_free()
