extends HBoxContainer

var path_to_script: String
var script_text: String



func get_data() -> Dictionary:
	return {"codename": $codename.text, "method": $method_name.text, "script": script_text, "path": path_to_script}


func _on_file_dialog_file_selected(path):
	var filename: String = path.split("\\")[-1]
	$select.text = "   " + filename + "   "
	
	path_to_script = path
	
	var script_file: FileAccess = FileAccess.open(path_to_script, FileAccess.READ)
	script_text = script_file.get_as_text()

func _on_select_pressed():
	$FileDialog.show()


func _on_del_pressed():
	queue_free()
