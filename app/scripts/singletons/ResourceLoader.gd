extends Node

const create_system_afex = "/structs/create_system"

const upload_image_afex = "/images/upload"
const download_image_afex = "/images/download"
const info_image_afex = "/images/info"

var http: HTTPRequest = HTTPRequest.new()
var base_address: String = "127.0.0.1:5000"



func _ready():
	add_child(http)


## Auth not required
func get_info() -> Dictionary:
	var headers: Array = ["Content-Type: application/json"]
	http.request(UrlUtils.build("http", Global.active_server["address"], "server_info"), headers, HTTPClient.METHOD_POST)
	var result = await http.request_completed
	if result[1] == 200:
		return JSON.parse_string(result[3].get_string_from_utf8())
	return {"error": true}


## Auth required
func get_image(filename: String) -> Dictionary:
	var cached_image = CacheUtils.get_image(filename)
	if cached_image["exists"]:
		return {"image": cached_image["image"]}
	var image_bytes: Dictionary = await UrlUtils.post("download_image", [], {"filename": filename}, "raw")
	if not image_bytes["Ok"]:
		return {"image": Image.new()}
	var image: Image = Image.new()
	image.load_webp_from_buffer(image_bytes["data"])
	CacheUtils.put_image(filename, image)
	return {"image": image}


## Auth required
func put_image(image: Image) -> String:
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--ImageBoundary\r\n".to_utf8_buffer())
	body.append_array("Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".to_utf8_buffer())
	body.append_array("Content-Type: image/webp\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer(true))
	body.append_array("\r\n--ImageBoundary--\r\n".to_utf8_buffer())
	var response: Dictionary = await UrlUtils.post_raw("upload_image", ["Content-Type: multipart/form-data; boundary=ImageBoundary"], body)
	if response["Ok"]:
		CacheUtils.put_image(response["filename"], image)
		return response["filename"]
	return ""


## Auth required
func create_system(system_name: String, system_codename: String, system_poster: String):
	var response: Dictionary = await UrlUtils.post("create_game_system", [], {"name": system_name, "codename": system_codename, "image_name": system_poster})
	if response["Ok"]:
		return true
	return false


## Auth required
func get_system(codename: String) -> Dictionary:
	var cached_system: Dictionary = CacheUtils.get_content('system/{0}'.format([codename]))
	var need_update: bool = false
	if cached_system["exists"]:
		var response: Dictionary = await UrlUtils.post("get_game_system_hash", [], {"codename": codename})
		if response["Ok"]:
			if response["hash"] == cached_system["hash"]:
				return cached_system["data"]
			else:
				need_update = true
	var response: Dictionary = await UrlUtils.post("get_game_system", [], {"codename": codename})
	if not response["Ok"]:
		return {}
	CacheUtils.put_content("system/{0}".format([codename]), response["hash"], response, need_update)
	return response


## Auth required
func get_systems(page: int) -> Array:
	var response = await UrlUtils.post("get_game_systems", [], {"page": page})
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
	var response = await UrlUtils.post("get_game_systems_count")
	if response["Ok"]:
		return response["count"]
	return 0


func get_categories(system_codename: String) -> Array:
	var response: Dictionary = await UrlUtils.post("get_categories", [], {"system_codename": system_codename})
	if response["Ok"]:
		return response["schemas"]
	return []
