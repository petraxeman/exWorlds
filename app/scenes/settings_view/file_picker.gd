extends HBoxContainer

var mouse_in: bool = false :
	set(value):
		_apply_theme()
		mouse_in = value

signal pressed
signal file_selected(filepath: String)
signal files_processed


func _ready():
	get_viewport().files_dropped.connect(_files_dropped)
	_apply_theme()

func _process(delta):
	mouse_in = _is_mouse_in_zone()


func _is_mouse_in_zone() -> bool:
	var mouse_pos = get_viewport().get_mouse_position()
	var global_rect = Rect2(global_position, size)
	return global_rect.has_point(mouse_pos)


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed and mouse_in:
				emit_signal("pressed")
				print("gggg")
				_apply_theme()


func _files_dropped(files: Array):
	if not mouse_in:
		return
	
	print(files)
	for filepath in files:
		emit_signal("file_selected", filepath)
		EXUtils.process_uploaded_file(filepath)
	emit_signal("files_processed")


func _apply_theme():
	if mouse_in:
		if Globals.current_theme.is_resource_exist("file-picker/hover"):
			$panel.add_theme_stylebox_override("panel", Globals.current_theme.get_resource("file-picker/hover")["data"])
	else:
		if Globals.current_theme.is_resource_exist("file-picker/normal"):
			$panel.add_theme_stylebox_override("panel", Globals.current_theme.get_resource("file-picker/normal")["data"])
