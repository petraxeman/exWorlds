extends Node

const create_system_afex = "/capi/create_system"

const upload_image_afex = "/mapi/upload_image"
const download_image_afex = "/mapi/download_image"
const fetch_image_afex = "/mapi/fetch_image"

var http: HTTPRequest = HTTPRequest.new()
var base_address: String = "127.0.0.1:5000"

signal image_uploaded
signal image_downloaded



func _ready():
	add_child(http)


func get_image(file_name: String):
	var cache: Array = Global.cache.select_rows("images", "file_name=\""+file_name + "\"", ["hash", "file_name", "image"])
	var headers: Array
	var result: Array
	if cache != []:
		var cached: Dictionary = cache[0]
		headers = ["token: 12312313", "image_name:" + file_name, "image_hash:" + cached["image_hash"]]
		http.request("http://" + base_address + fetch_image_afex, headers, HTTPClient.METHOD_POST)
		result = await http.request_completed
		if result[1] == 200 and JSON.parse_string(result[3]).get("result", 100) == 1:
			var image: Image = Image.new()
			var _err = image.load_webp_from_buffer(cached["image"])
			return image
	elif cache == [] or result[1] != 200 or JSON.parse_string(result[3]).get("result", 100) != 1:
		headers = ["token:123123123", "image_name:"+file_name]
		http.request("http://" + base_address + download_image_afex, headers, HTTPClient.METHOD_POST)
		result = await http.request_completed
		if result[1] == 200:
			print(result)
			#Global.cache.update_rows("images", "file_name="+file_name, {""})
			#var image = Image.new()
			#var err = image.load_webp_from_buffer(result[3])
			#if err == OK:
			#	return image
	return null

func put_image(image: Image):
	var file_name: String = "image.png"
	var url = "http://" + base_address + upload_image_afex
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--BodyBoundaryHere\r\n".to_utf8_buffer())
	body.append_array(("Content-Disposition: form-data; name=\"file\"; file_name=" + file_name + "\r\n").to_utf8_buffer())
	body.append_array("Content-Type: image/png\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer())
	body.append_array("\r\n--BodyBoundaryHere--\r\n".to_utf8_buffer())
	
	var headers: Array = ["token: 123123123", "Content-Type: multipart/form-data; boundary=BodyBoundaryHere"]
	http.request_raw(url, headers, HTTPClient.METHOD_POST, body)
	var result = await http.request_completed
	result[3] = result[3].get_string_from_utf8()
	print(result)
	if result[1] == 200 and JSON.parse_string(result[3]).get("result", 100) == 1:
		var data = JSON.parse_string(result[3])
		Global.cache.insert_row("images", {"hash": data["hash"], "file_name": data["file_name"], "image": image.save_webp_to_buffer()})
		var r = await get_image(data["file_name"] + "asd")
		print(r)
