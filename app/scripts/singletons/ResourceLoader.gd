extends Node

const create_system_afex = "/structs/create_system"

const upload_image_afex = "/images/upload"
const download_image_afex = "/images/download"
const info_image_afex = "/images/info"

var http: HTTPRequest = HTTPRequest.new()
var base_address: String = "127.0.0.1:5000"

signal image_uploaded
signal image_downloaded



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
	var cache: Array = Global.cache.select_rows("images", "file_name=\"" + file_name + "\"", ["author", "file_name", "image"])
	if cache != []:
		var cached: Dictionary = cache[0]
		var image: Image = Image.new()
		var _error = image.load_webp_from_buffer(cached["image"])
		return {"author": cached["author"], "image": image}
	else:
		var auth_data = Global.get_auth_data()
		var headers = auth_data["headers"]
		var image_info: Dictionary
		http.request(UrlEnum.build("http", auth_data["addr"], "image_info"), headers, HTTPClient.METHOD_POST)
		var image_info_result = await http.request_completed
		image_info = JSON.parse_string(image_info_result[3].get_string_from_utf8())
		http.request(UrlEnum.build("http", auth_data["addr"], "image_download"), headers, HTTPClient.METHOD_POST)
		var image_result = await http.request_completed
		if image_info_result[1] != 200 or image_result[1] != 200:
			return {"author": "undefined", "image": Image.new()}
		var new_image = Image.new()
		new_image.load_webp_from_buffer(image_result[3])
		return {"author": image_info["author"], "image": new_image}
	return {"author": "undefined", "image": Image.new()}


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
