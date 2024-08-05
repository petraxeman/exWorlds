extends HBoxContainer

var script_filename: String
var path_to_script: String



func get_data() -> Array:
	return [script_filename, path_to_script]


func _on_file_dialog_file_selected(path):
	var filename: String = path.split("\\")[-1]
	$select.text = "   " + filename + "   "
	
	script_filename = filename
	path_to_script = path


func _on_select_pressed():
	$FileDialog.show()


func _on_del_pressed():
	queue_free()
