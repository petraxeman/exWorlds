extends Node
class_name UrlLib

const endpoints: Dictionary = {
	# Auth
	"auth": "/account/auth",
	"registration": "/account/registration",
	"add_user_to_queue": "/account/addUserToQueue",
	# Server
	"server_info": "/server/info",
	# Images
	"upload_image": "/image/upload",
	"info_image": "/image/info",
	"download_image": "/image/download",
	# Macros
	"macro_upload": "/macro/upload",
	"macro_get": "/macro/get",
	# Game Systems
	"create_game_system": "/gameSystem/create",
	"get_game_system": "/gameSystem/get",
	"get_game_system_hash": "/gameSystem/getHash",
	"get_game_systems": "/gameSystems/get",
	"get_game_systems_count": "/gameSystems/getCount",
	"delete_game_system": "/gameSystems/delete",
	# Categories
	"get_tables": "/gameSystem/getTables",
	"get_table": "/gameSystem/getTable",
	"get_table_hash": "/gameSystem/getTableHash",
	"create_table": "/gameSystem/createTable",
	"delete_table": "/gameSystem/deleteTable"
}



static func build(proto: String, url: String, endpoint: String):
	return proto + "://" + url + endpoints[endpoint]


static func post(endpoint: String,
				additional_headers: Array = [],
				body: Dictionary = {},
				expecting: String = "json",
				auth_required: bool = true):
	var http: HTTPRequest = HTTPRequest.new()
	Global.add_child(http)
	var headers: Array
	if auth_required:
		headers = ["Auth-Token: {0}".format([Global.active_server["token"]]), "Content-Type: application/json"]
	headers += ["Content-Type: application/json"]
	headers += additional_headers
	http.request(
		UrlLib.build(Global.proto, Global.active_server["address"], endpoint),
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
		UrlLib.build(Global.proto, Global.active_server["address"], endpoint),
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
