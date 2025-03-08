extends PanelContainer

var mouse_in: bool = false
var is_selected: bool = false
var uuid: String
@onready var apply_theme_from = $margin/hbox

signal selected(uuid: String)
signal unselected(uuid: String)
signal doubleclick(uuid: String)

enum {ALL_GOOD, CANT_CONNECT, SOMTHING_WRONG}



func _ready() -> void:
	ThemeHandler.current_theme.apply_theme(apply_theme_from)
	_apply_theme()


func setup(sname: String, mark: String, addr: String, sts: int = CANT_CONNECT, exuuid: String = "0"):
	set_names(sname, mark)
	set_addr(addr)
	set_status(sts)
	uuid = exuuid


func set_names(sname: String, mark: String):
	if mark:
		if not sname:
			sname = "Undefined server"
		$margin/hbox/base_info/title/server_name.text = mark
		$margin/hbox/base_info/title/server_orig.text = "(%s)" % sname
	elif sname:
		$margin/hbox/base_info/title/server_name.text = sname
	else:
		$margin/hbox/base_info/title/server_name.text = "Undefined server"


func set_addr(addr: String):
	$margin/hbox/base_info/server_addr.text = addr


func set_status(sts: int):
	match sts:
		ALL_GOOD:
			$margin/hbox/status/status_light.modulate = Color(0.333, 0.89, 0.396)
		CANT_CONNECT:
			$margin/hbox/status/status_light.modulate = Color(1, 0.839, 0.341)
		SOMTHING_WRONG:
			$margin/hbox/status/status_light.modulate = Color(0.839, 0, 0)


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if not event.double_click and not event.pressed:
				if mouse_in:
					emit_signal("selected", uuid)
				else:
					emit_signal("unselected", uuid)
				_apply_theme()
			elif event.double_click and event.pressed:
				if mouse_in:
					print("IS DOUBLE CLICK")
					emit_signal("doubleclick", uuid)


func _on_mouse_entered() -> void:
	mouse_in = true
	_apply_theme()


func _on_mouse_exited() -> void:
	mouse_in = false
	_apply_theme()


func _apply_theme():
	if is_selected:
		if ThemeHandler.current_theme.is_resource_exist("server-item/selected"):
			add_theme_stylebox_override("panel", ThemeHandler.current_theme.get_resource("server-item/selected")["data"])
		return
	elif mouse_in:
		if ThemeHandler.current_theme.is_resource_exist("server-item/hover"):
			add_theme_stylebox_override("panel", ThemeHandler.current_theme.get_resource("server-item/hover")["data"])
		return
	else:
		if ThemeHandler.current_theme.is_resource_exist("server-item/normal"):
			add_theme_stylebox_override("panel", ThemeHandler.current_theme.get_resource("server-item/normal")["data"])
	
