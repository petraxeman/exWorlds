extends Node
class_name ZipUtils



static func unzip(path_to_zip: String, extract_to: String) -> void:
	var zr : ZIPReader = ZIPReader.new()
	
	if zr.open(path_to_zip) == OK:		
		for filepath in zr.get_files():
			var zip_directory : String = path_to_zip.get_base_dir()
		
			var da : DirAccess = DirAccess.open(extract_to)
			
			da.make_dir_recursive(filepath.get_base_dir())
			
			var fa : FileAccess = FileAccess.open("%s/%s" % [extract_to, filepath], FileAccess.WRITE)
			if fa:
				fa.store_buffer(zr.read_file(filepath))


static func is_archive(path: String) -> bool:
	var file_extension = path.get_extension().to_lower()
	return file_extension == "zip"
