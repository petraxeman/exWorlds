extends MarginContainer

signal pressed
const threshold: int = 100



func _ready():
	modulate = Color(1, 1, 1, 0)


func _input(event):
	if event is InputEventMouseMotion:
		var mouse_position: Vector2 = event.get_position()
		var pos: Vector2 = global_position + (size / 2)
		if mouse_position.x > pos.x - threshold and mouse_position.x < pos.x + threshold and \
		mouse_position.y > pos.y - threshold and mouse_position.y < pos.y + threshold:
			modulate = Color(1, 1, 1, 1)
		elif self.is_visible():
			modulate = Color(1, 1, 1, 0)


func _on_add_button_pressed():
	emit_signal("pressed")
