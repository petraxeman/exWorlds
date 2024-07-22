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
		return cached_image["image"]
	var image_bytes: Dictionary = await UrlUtils.post("download_image", [], {"filename": filename}, "raw")
	if image_bytes["Ok"]:
		return {"image": Image.new()}
	var image: Image = Image.new()
	image.load_webp_from_buffer(image_bytes["data"])
	CacheUtils.put_image(filename, image)
	return {"image": image}


## Auth required
func put_image(image: Image) -> bool:
	var body: PackedByteArray = PackedByteArray()
	body.append_array("\r\n--ImageBoundary\r\n".to_utf8_buffer())
	body.append_array("Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".to_utf8_buffer())
	body.append_array("Content-Type: image/webp\r\n\r\n".to_utf8_buffer())
	body.append_array(image.save_webp_to_buffer(true))
	body.append_array("\r\n--ImageBoundary--\r\n".to_utf8_buffer())
	var response: Dictionary = await UrlUtils.post_raw("upload_image", ["Content-Type: multipart/form-data; boundary=ImageBoundary"], body)
	if response["Ok"]:
		CacheUtils.put_image(response["filename"], image)
		return true
	return false


## Auth required
func create_system(system_name: String, system_codename: String, system_poster: String):
	var response: Dictionary = await UrlUtils.post("create_game_system", [], {"name": system_name, "codename": system_codename, "image_name": system_poster})
	if response["Ok"] == 200:
		return true
	return false


## Auth required
func get_system(codename: String) -> Dictionary:
	var cached_system: Dictionary = CacheUtils.get_content('system/{0}'.format(codename))
	if cached_system["exists"]:
		var response: Dictionary = await UrlUtils.post("get_game_system_hash")
		if response["Ok"]:
			if response["hash"] == cached_system["hash"]:
				return cached_system["data"]
	
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
	var response = await UrlUtils.post("get_game_systems", [], {"page": page})
	if not response["Ok"]:
		return []
	var systems: Array = []
	for codename in response["systems"]:
		var system = await get_system(codename)
		system["image"] = await get_image(system["image_name"])
		systems.append(system)
	return systems


## Auth required
func get_systems_count() -> int:
	var auth_data = Global.get_auth_data()
	var result = await UrlEnum.post(
		http,
		UrlEnum.build("http", auth_data["addr"], "get_game_systems_count"),
		auth_data["headers"],
		{}
		)
	if result["r"] == "Ok":
		return result["count"]
	return 0


func get_categories(system_codename: String) -> Array:
	var response: Dictionary = await UrlUtils.post("get_categories", [], {"system_codename": system_codename})
	if response["Ok"]:
		return response["schemas"]
	return []
