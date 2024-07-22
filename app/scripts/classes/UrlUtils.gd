extends Node
class_name UrlUtils

const endpoints: Dictionary = {
	# Common
	"auth": "/account/auth",
	"registration": "/account/registration",
	"server_info": "/server/info",
	# Images
	"upload_image": "/images/upload",
	"info_image": "/images/info",
	"download_image": "/images/download",
	# Game Systems
	"create_game_system": "/structs/system/create",
	"get_game_system": "/structs/system/get",
	"get_game_system_hash": "/structs/system/getHash",
	"get_game_systems": "/structs/systems/get",
	"get_game_systems_count": "/structs/systems/getCount",
	# Categories
	"get_categories": "/structs/schemas/get"
}



static func build(proto: String, url: String, endpoint: String):
	return proto + "://" + url + endpoints[endpoint]


static func post(endpoint: String, additional_headers: Array = [], body: Dictionary = {}, expecting: String = "json"):
	var http: HTTPRequest = HTTPRequest.new()
	Global.add_child(http)
	var headers: Array = ["Auth-Token: {0}".format([Global.active_server["token"]]), "Content-Type: application/json"]
	headers += additional_headers
	http.request(
		UrlUtils.build(Global.proto, Global.active_server["address"], endpoint),
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
		)
	var result = await http.request_completed
	http.queue_free()
	if result[1] == 200:
		if expecting == "json":
			var data = JSON.parse_string(result[3].get_string_from_utf8())
			data["Ok"] = true
			return data
		elif expecting == "raw":
			return {"Ok": true, "data": result[3]}
	return {"Ok": false}


static func post_raw(endpoint: String, additional_headers: Array, body: PackedByteArray, expecting: String = "json"):
	var http: HTTPRequest = HTTPRequest.new()
	Global.add_child(http)
	var headers: Array = ["Auth-Token: {0}".format([Global.active_server["token"]]), "Content-Type: application/json"]
	headers += additional_headers
	http.request_raw(
		UrlUtils.build(Global.proto, Global.active_server["address"], endpoint),
		headers,
		HTTPClient.METHOD_POST,
		body
		)
	var result = await http.request_completed
	http.queue_free()
	if result[1] == 200:
		if expecting == "json":
			var data = JSON.parse_string(result[3].get_string_from_utf8())
			data["Ok"] = true
			return data
		elif expecting == "raw":
			return {"Ok": true, "data": result[1]}
	return {"Ok": false}
