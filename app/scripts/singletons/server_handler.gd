extends Node

const endpoints: Dictionary = {
	# Auth
	"auth": "/api/login",
	"registration": "/api/register",
	# Common
	"server_info": "/api/server/info",
}

var current_server: String
var http: HTTPRequest
var addr_re: RegEx = RegEx.create_from_string(r"^(?<proto>http:\/\/|https:\/\/)?(?<address>[^\s]*)$")


func _ready() -> void:
	http = HTTPRequest.new()


func set_address():
	pass


func parse_address(_addr: String):
	var result = addr_re.search(_addr)
	var prepared: Dictionary = {}
	
	if not result:
		return {"addr": "", "proto": ""}
	for n in result.names:
		prepared[n] = result.strings[result.names[n]]
	
	if not prepared.get("proto"):
		prepared["proto"] = "https://"
	
	return prepared


func build(url: String, endpoint: String):
	return url + endpoints[endpoint]


func post(endpoint: String,
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
		build(Globals.current_server.get("addr"), endpoint),
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


func post_raw(endpoint: String, additional_headers: Array, body: PackedByteArray, expecting: String = "json"):
	var http: HTTPRequest = HTTPRequest.new()
	Globals.add_child(http)
	var headers = ["Auth-Token: %s" % Globals.current_server["token"], "Content-Type: application/json"]
	headers += additional_headers
	http.request_raw(
		build(Globals.current_server["addr"], endpoint),
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
