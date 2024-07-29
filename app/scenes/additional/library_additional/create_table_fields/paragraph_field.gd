extends PanelContainer

var parent: Node
@onready var fields: Dictionary = {
	"name": $margin/vbox/args_row_1/name/entry,
	"codename": $margin/vbox/args_row_1/codename/entry,
	"default": $margin/vbox/args_row_1/default/entry,
	"placeholder": $margin/vbox/args_row_1/placeholder/entry,
	"hide_filed": $margin/vbox/args_row_2/hide_field/check,
	"hide_name": $margin/vbox/args_row_2/hide_if_empty/check,
	"hide_if_empty": $margin/vbox/args_row_2/hide_if_empty/check,
}



func get_data() -> Dictionary:
	if not $margin/vbox/args_row_1/name/entry.text or not $margin/vbox/args_row_1/codename/entry.text:
		return {"Ok": false}
	var base: Dictionary = {}
	for field in fields:
		if fields[field] is CheckButton and fields[field].button_pressed:
			base[field] = int(fields[field].button_pressed)
		elif fields[field] is LineEdit and fields[field].text != "":
			base[field] = fields[field].text
	base["Ok"] = true
	return base



func _on_clone_pressed():
	pass # Replace with function body.


func _on_delete_pressed():
	queue_free()


