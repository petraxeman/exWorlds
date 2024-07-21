extends Node
class_name UrlEnum

const endpoints: Dictionary = {
	# Common
	"auth": "/account/auth",
	"registration": "/account/registration",
	"server_info": "/server/info",
	# Images
	"put_image": "/images/upload",
	"info_image": "/images/info",
	"download_image": "/images/download",
	# Game Systems
	"create_game_system": "/structs/system/create",
	"get_game_system": "/structs/system/get",
	"get_game_system_hash": "/structs/system/getHash",
	"get_game_systems": "/structs/systems/get",
	"get_game_systems_count": "/structs/systems/getCount"
}



static func build(proto: String, url: String, endpoint: String):
	return proto + "://" + url + endpoints[endpoint]


static func post(_http: HTTPRequest, url: String, headers: Array, body: Dictionary) -> Dictionary:
	var http = HTTPRequest.new()
	Global.add_child(http)
	http.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	var result = await http.request_completed
	http.queue_free()
	if result[1] == 200:
		var data = JSON.parse_string(result[3].get_string_from_utf8())
		data["r"] = "Ok"
		return data
	return {"r": "Error"}
