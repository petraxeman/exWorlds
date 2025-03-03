extends Node
class_name UrlLib

const endpoints: Dictionary = {
	# Auth
	"auth": "/account/auth",
	"registration": "/account/registration",
	# Server
	"server_info": "/server/info",
}



static func build(url: String, endpoint: String):
	return url + endpoints[endpoint]


static func post(endpoint: String,
				additional_headers: Array = [],
				body: Dictionary = {},
				expecting: String = "json",
				auth_required: bool = true):
	var http: HTTPRequest = HTTPRequest.new()
	Globals.add_child(http)
	var headers: Array
	if auth_required:
		headers = ["Auth-Token: %s" % Globals.current_server["token"], "Content-Type: application/json"]
	headers += ["Content-Type: application/json"]
	headers += additional_headers
	http.request(
		UrlLib.build(Globals.current_server.get("addr"), endpoint),
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
	print(JSON.parse_string(result[3].get_string_from_utf8()))
	return {"Ok": false}


static func post_raw(endpoint: String, additional_headers: Array, body: PackedByteArray, expecting: String = "json"):
	var http: HTTPRequest = HTTPRequest.new()
	Globals.add_child(http)
	var headers = ["Auth-Token: %s" % Globals.current_server["token"], "Content-Type: application/json"]
	headers += additional_headers
	http.request_raw(
		UrlLib.build(Globals.current_server["addr"], endpoint),
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
