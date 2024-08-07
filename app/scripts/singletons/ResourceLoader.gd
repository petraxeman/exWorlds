extends Node

const create_system_afex = "/structs/create_system"

const upload_image_afex = "/images/upload"
const download_image_afex = "/images/download"
const info_image_afex = "/images/info"



## Auth not required
func get_info() -> Dictionary:
	var result: Dictionary = await UrlLib.post("server_info", [], {}, "json", false)
	if result["Ok"]:
		return result
	return {}


## Auth required
func get_image(image_name: String) -> Dictionary:
	var cached_image = Global.cache.get_image(image_name)
	if cached_image["Ok"]:
		return {"image": cached_image["image"]}
	var image_bytes: Dictionary = await UrlLib.post("download_image", [], {"filename": image_name}, "raw")
	if not image_bytes["Ok"]:
		return {"image": Image.new()}
	var image: Image = Image.new()
	image.load_webp_from_buffer(image_bytes["data"])
	Global.cache.put_image(image_name, image)
	return {"image": image}


## Auth required
func put_image(image: Image) -> String:
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--ImageBoundary\r\n".to_utf8_buffer())
	body.append_array("Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".to_utf8_buffer())
	body.append_array("Content-Type: image/webp\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer(true))
	body.append_array("\r\n--ImageBoundary--\r\n".to_utf8_buffer())
	var response: Dictionary = await UrlLib.post_raw("upload_image", ["Content-Type: multipart/form-data; boundary=ImageBoundary"], body)
	if response["Ok"]:
		Global.cache.put_image(response["filename"], image)
		return response["filename"]
	return ""


## Auth required
func create_system(system_name: String, system_codename: String, system_poster: String):
	var response: Dictionary = await UrlLib.post("create_game_system", [], {"name": system_name, "codename": system_codename, "image_name": system_poster})
	if response["Ok"]:
		return true
	return false


## Auth required
func get_system(codename: String) -> Dictionary:
	var cached_system: Dictionary = Global.cache.get_content('system/{0}'.format([codename]))
	var need_update: bool = false
	if cached_system["Ok"]:
		var response: Dictionary = await UrlLib.post("get_game_system_hash", [], {"codename": codename})
		if response["Ok"]:
			if response["hash"] == cached_system["hash"]:
				return cached_system["data"]
			else:
				need_update = true
	var response: Dictionary = await UrlLib.post("get_game_system", [], {"codename": codename})
	if not response["Ok"]:
		return {}
	Global.cache.put_content("system/{0}".format([codename]), response["hash"], response, need_update)
	return response


## Auth required
func get_systems(page: int) -> Array:
	var response = await UrlLib.post("get_game_systems", [], {"page": page})
	if not response["Ok"]:
		return []
	var systems: Array = []
	for codename in response["systems"]:
		var system = await get_system(codename)
		
		system["image"] = await get_image(system["image_name"])
		system["image"]["filename"] = system["image_name"]
		system.erase("image_name")
		
		systems.append(system)
	return systems


## Auth required
func get_systems_count() -> int:
	var response = await UrlLib.post("get_game_systems_count")
	if response["Ok"]:
		return response["count"]
	return 0


#
# TABLE ACTIONS
#

# GET ALL TABLES IN SYSTEM 
func get_tables(system_codename: String) -> Array:
	var response: Dictionary = await UrlLib.post("get_tables", [], {"system_codename": system_codename})
	if response["Ok"]:
		return response["schemas"]
	return []


# CREATE NEW TABLE
func create_table(data: Dictionary, system_name: String):
	var response: Dictionary = await UrlLib.post("create_table", ["Game-System: %s"%system_name], data)
	if response["Ok"]:
		Global.cache.put_content("(type=table,system_name={0},table_name={1})".format([system_name, data["common"]["table_codename"]]), response["hash"], data)
		return true
	return false
