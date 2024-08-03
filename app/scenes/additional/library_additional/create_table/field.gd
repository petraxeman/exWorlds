extends PanelContainer

signal change_field
signal delete_field

var field_type: String = "Undefined"
var codename: String = ""
var field_name: String = ""



func render_name():
	$label.text = "%s <%s>" % [field_type, codename]


func set_data(ft: String, cn: String, fn: String) -> void:
	field_type = ft
	codename = cn
	field_name = fn
	render_name()


func _on_settings_pressed():
	emit_signal("change_field")


func _on_delete_pressed():
	emit_signal("delete_field")
