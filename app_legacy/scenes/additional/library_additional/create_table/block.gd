extends VBoxContainer

signal change_block
signal delete_block

var block_name: String = ""



func set_block_name(bn: String):
	block_name = bn
	$label.text = "Block %s" % bn


func _on_settings_pressed():
	emit_signal("change_block")


func _on_delete_pressed():
	emit_signal("delete_block")
