extends Node
class_name EXUtils



static func array_to_color(arr: Array) -> Color:
	if arr.size() == 3:
		return Color(arr[0], arr[1], arr[2])
	elif arr.size() == 4:
		return Color(arr[0], arr[1], arr[2], arr[3])
	return Color(0, 0, 0)


static func disconnect_all(node: Node):
	for conn in node.get_incoming_connections():
		node.disconnect(conn["signal"], conn["callable"])


static func disconnect_all_pressed(node: Button):
	for conn in node.pressed.get_connections():
		node.pressed.disconnect(conn["callable"])


static func clear_temp():
	for dir in DirAccess.get_directories_at("user://temp"):
		DirAccess.remove_absolute("user://temp/%s" % dir)
	
	for file in DirAccess.get_files_at("user://temp"):
		DirAccess.remove_absolute("user://temp/%s" % file)


static func process_uploaded_file(filepath: String):
	if ZipUtils.is_archive(filepath):
		process_uploaded_zip(filepath)


static func process_uploaded_zip(filepath: String):
	ZipUtils.unzip(filepath, "user://temp/")
	for dir in DirAccess.get_directories_at("user://temp"):
		if FileAccess.file_exists("user://temp/" + dir + "/theme.json"):
			DirAccess.rename_absolute("user://temp/" + dir, "user://themes/" + uuid4.v4())


static func copy_directory_recursively(from: String, to: String) -> void:
	if not DirAccess.dir_exists_absolute(to):
		DirAccess.make_dir_recursive_absolute(to)
	
	var directory: DirAccess = DirAccess.open(from)
	
	if directory:
		directory.list_dir_begin()
		var file_name = directory.get_next()
		while (file_name != "" && file_name != "." && file_name != ".."):
			if directory.current_is_dir():
				copy_directory_recursively("%s/%s" % [from, file_name], "%s/%s" % [to, file_name])
			else:
				directory.copy("%s/%s" % [from, file_name], "%s/%s" % [to, file_name])
			file_name = directory.get_next()
	else:
		push_warning("Error copying " + from + " to " + to)
