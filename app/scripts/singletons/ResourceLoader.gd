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


func get_image(file_name: String):
	var cache: Array = Global.cache.select_rows("images", "file_name=\"" + file_name + "\"", ["hash", "file_name", "image"])
	var image_info: Dictionary = {"empty": true}
	if cache != [] and false:
		var cached: Dictionary = cache[0]
		var headers = ["token: 12312313", "Image-Name:" + file_name]
		http.request("http://" + base_address + info_image_afex, headers, HTTPClient.METHOD_POST)
		var result = await http.request_completed
		image_info = JSON.parse_string(result[3].get_string_from_utf8())
		if result[1] == 200 and image_info["result"] == 1 and image_info["image_hash"] == cached["hash"]:
			var image: Image = Image.new()
			var _error = image.load_webp_from_buffer(cached["image"])
			return image
	
	var headers = ["token: 12312313", "Image-Name:" + file_name]
	if image_info["empty"]:
		http.request("http://" + base_address + info_image_afex, headers, HTTPClient.METHOD_POST)
		var result = await http.request_completed
		image_info = JSON.parse_string(result[3].get_string_from_utf8())
	http.request("http://" + base_address + download_image_afex, headers, HTTPClient.METHOD_POST)
	var result = await http.request_completed
	if result[1] == 200:
		var new_image = Image.new()
		new_image.load_webp_from_buffer(result[3])
		return new_image
	return Image.new()


func put_image(image: Image):
	var url = "http://" + base_address + upload_image_afex
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--ImageBoundary\r\n".to_utf8_buffer())
	body.append_array("Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".to_utf8_buffer())
	body.append_array("Content-Type: image/webp\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer(true))
	body.append_array("\r\n--ImageBoundary--\r\n".to_utf8_buffer())
	var headers: Array = [
		"token: 123123123",
		"Content-Type: multipart/form-data; boundary=ImageBoundary"]
	http.request_raw(url, headers, HTTPClient.METHOD_POST, body)
	var result = await http.request_completed
	result[3] = result[3].get_string_from_utf8()
	if result[1] == 200 and JSON.parse_string(result[3]).get("result", 100) == 1:
		var data = JSON.parse_string(result[3])
		Global.cache.insert_row("images", {"hash": data["hash"], "file_name": data["file_name"], "image": image.save_webp_to_buffer(true)})
		return data["file_name"]


func create_system(system_name: String, system_codename: String, system_poster: String):
	var data: Dictionary = {"name": system_name, "codename": system_codename, "poster": system_poster}
	http.request("http://"+base_address+create_system_afex, ["Token:123123"], HTTPClient.METHOD_POST, str(data))
	var result = await http.request_completed
