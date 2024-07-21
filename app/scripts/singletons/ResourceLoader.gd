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
	var auth_data: Dictionary = Global.get_auth_data()
	var headers: Array = ["Content-Type: application/json"]
	http.request(UrlEnum.build("http", auth_data["addr"], "server_info"), headers, HTTPClient.METHOD_POST)
	var result = await http.request_completed
	if result[1] == 200:
		return JSON.parse_string(result[3].get_string_from_utf8())
	return {"error": true}


## Auth required
func get_image(file_name: String) -> Dictionary:
	var cache: Array = Global.cache.select_rows("images", "file_name=\"" + file_name + "\"", ["file_name", "image"])
	if cache != []:
		var cached: Dictionary = cache[0]
		var image: Image = Image.new()
		var _error = image.load_webp_from_buffer(cached["image"])
		return {"image": image}
	var auth_data = Global.get_auth_data()
	var headers = auth_data["headers"]
	headers.append("Image-Name:"+file_name)
	var image_info: Dictionary
	http.request(UrlEnum.build("http", auth_data["addr"], "info_image"), headers, HTTPClient.METHOD_POST)
	var image_info_result = await http.request_completed
	image_info = JSON.parse_string(image_info_result[3].get_string_from_utf8())
	http.request(UrlEnum.build("http", auth_data["addr"], "download_image"), headers, HTTPClient.METHOD_POST)
	var image_result = await http.request_completed
	if image_info_result[1] != 200 or image_result[1] != 200:
		return {"author": "undefined", "image": Image.new()}
	var new_image: Image = Image.new()
	new_image.load_webp_from_buffer(image_result[3])
	Global.cache.insert_row("images", {"file_name": file_name, "image": new_image.save_webp_to_buffer(true)})
	return {"author": image_info["author"], "image": new_image}


## Auth required
func put_image(image: Image) -> String:
	var auth_data: Dictionary = Global.get_auth_data()
	var headers: Array = auth_data["headers"]
	headers.append("Content-Type: multipart/form-data; boundary=ImageBoundary")
	var url: String = UrlEnum.build("http", auth_data["addr"], "put_image")
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--ImageBoundary\r\n".to_utf8_buffer())
	body.append_array("Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".to_utf8_buffer())
	body.append_array("Content-Type: image/webp\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer(true))
	body.append_array("\r\n--ImageBoundary--\r\n".to_utf8_buffer())
	http.request_raw(url, headers, HTTPClient.METHOD_POST, body)
	var result = await http.request_completed
	result[3] = result[3].get_string_from_utf8()
	if result[1] == 200:
		var data = JSON.parse_string(result[3])
		Global.cache.insert_row("images", {"author": data["author"], "file_name": data["name"], "image": image.save_webp_to_buffer(true)})
		return data["name"]
	return "Somthing wrong"


## Auth required
func create_system(system_name: String, system_codename: String, system_poster: String):
	var data: String = JSON.stringify({"name": system_name, "codename": system_codename, "image_name": system_poster})
	var auth_data: Dictionary = Global.get_auth_data()
	http.request(UrlEnum.build("http", auth_data["addr"], "create_game_system"), auth_data["headers"], HTTPClient.METHOD_POST, data)
	var result = await http.request_completed
	if result[1] == 200:
		return true
	return false


## Auth required
func get_system(codename: String) -> Dictionary:
	var update_row = false
	var cache = Global.cache.select_rows("requests", 'request="system/%s"' % codename, ["hash", "data"])
	var auth_data = Global.get_auth_data()
	if cache != []:
		var hash_response: Dictionary = await UrlEnum.post(
			http,
			UrlEnum.build("http", auth_data["addr"], "get_game_system_hash"),
			auth_data["headers"],
			{"codename": codename}
			)
		if hash_response.get("r", "Error") == "Ok" and hash_response["hash"] == cache[0]["hash"]:
			var cached_data: Dictionary = JSON.parse_string(cache[0]["data"])
			return cached_data
		else:
			update_row = true
	var new_data: Dictionary = await UrlEnum.post(
		http,
		UrlEnum.build("http", auth_data["addr"], "get_game_system"),
		auth_data["headers"],
		{"codename": codename}
	)
	if update_row:
		Global.cache.update_rows("requests", 'request="system/%s"' % codename, {"hash": new_data["hash"], "data": JSON.stringify(new_data)})
	else:
		Global.cache.insert_row("requests", {"request": "system/%s" % codename, "hash": new_data["hash"], "data": JSON.stringify(new_data)})
	return new_data


## Auth required
func get_systems(page: int) -> Array:
	var auth_data = Global.get_auth_data()
	var systems = await UrlEnum.post(
		http,
		UrlEnum.build("http", auth_data["addr"], "get_game_systems"),
		auth_data["headers"],
		{"page": page}
		)
	if systems.get("r", "Error") != "Ok":
		return []
	var loaded_system: Array = []
	for codename in systems["systems"]:
		var system = await get_system(codename)
		system["image"] = await get_image(system["image_name"])
		loaded_system.append(system)
	return loaded_system
