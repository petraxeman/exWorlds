extends MarginContainer

signal button_pressed



func _input(event):
	var lower_border = self.global_position
	var upper_border = self.global_position + self.size
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and \
		(event.position.x > lower_border.x) and (event.position.y > lower_border.y) and \
		(event.position.x < upper_border.x) and (event.position.y < upper_border.y):
		emit_signal("button_pressed")


func set_icon(icon_name: String):
	$panel/margin/hbox/icon.texture = IconEnum.get_image_texture(icon_name)


func set_texture(texture: ImageTexture):
	$panel/margin/hbox/icon.texture = texture


func set_label(text: String):
	$panel/margin/hbox/name.text = text
