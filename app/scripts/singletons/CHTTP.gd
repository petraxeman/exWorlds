extends Node


var base_address = "127.0.0.1:5000"
var http: HTTPRequest



func _ready():
	http = HTTPRequest.new()
	add_child(http)


func upload_image(image: Image) -> String:
	var file_name: String = "image.png"
	var url = "http://" + base_address + upload_image_afex
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--BodyBoundaryHere\r\n".to_utf8_buffer())
	body.append_array(("Content-Disposition: form-data; name=\"file\"; filename=" + file_name + "\r\n").to_utf8_buffer())
	body.append_array("Content-Type: image/png\r\n\r\n".to_utf8_buffer())
	body.append_array(image.get_data())
	body.append_array("\r\n--BodyBoundaryHere--\r\n".to_utf8_buffer())
	
	var headers: Array = ["token: 123123123", "Content-Type: multipart/form-data; boundary=BodyBoundaryHere"]
	http.request_raw(url, headers, HTTPClient.METHOD_POST, body)
	var result = await http.request_completed
	result[3] = result[3].get_string_from_utf8()
	if result[1] == 200 and JSON.parse_string(result[3]).get("result", 100) == 1:
		return result[3]["image_name"]
	return ""


func download_image() -> Image:
	return Image.new()


func create_new_system(sname: String, cname: String, image: PackedByteArray) -> bool:
	#var headers: Array = ["token:" + Global.servers[Global.active_server]["token"]]
	var headers = ["content:111"]
	var url = "http://127.0.0.1:5000/capi/create_system"
	#var url: String = "http://" + Global.servers[Global.active_server]["address"] + create_system_afex
	var data = {"name": sname, "code_name": cname, "image": Marshalls.raw_to_base64(image)}
	http.request(url, headers, HTTPClient.METHOD_POST, str(data))
	await http.request_completed
	print("Sended")
	return false
