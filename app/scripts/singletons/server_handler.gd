extends Node

const endpoints: Dictionary = {
	# Auth
	"auth": "/api/login",
	"registration": "/api/register",
	# Common
	"server-info": "/api/server/info",
}

var current_server: Dictionary
var server_uuid: String
var server_address: String
var http: HTTPRequest
var addr_re: RegEx = RegEx.create_from_string(r"^(?<proto>http:\/\/|https:\/\/)?(?<address>[^\s]*)$")


func _ready() -> void:
	http = HTTPRequest.new()
	add_child(http)


func set_server(server: Dictionary, suuid: String):
	current_server = server
	server_uuid = suuid
	
	var prepared_addr = parse_address(current_server["addr"])
	server_address = prepared_addr["proto"] + prepared_addr["address"]


func parse_address(raw_addr: String):
	var result = addr_re.search(raw_addr)
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
	
	var headers: Array = []
	if auth_required:
		headers = ["Auth-Token: %s" % current_server["token"]]
	headers += ["Content-Type: application/json"]
	headers += additional_headers
	
	http.request(
		build(server_address, endpoint),
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
		)
	var result = await http.request_completed
	if result[1] == 200:
		if expecting == "json":
			var data = JSON.parse_string(result[3].get_string_from_utf8())
			print(data)
			data["Ok"] = true
			return data
		elif expecting == "raw":
			return {"Ok": true, "data": result[3]}
	return {"Ok": false}


func post_raw(endpoint: String, additional_headers: Array, body: PackedByteArray, expecting: String = "json"):
	var headers = ["Auth-Token: %s" % Globals.current_server["token"], "Content-Type: application/json"]
	headers += additional_headers
	http.request_raw(
		build(Globals.current_server["addr"], endpoint),
		headers,
		HTTPClient.METHOD_POST,
		body
		)
	var result = await http.request_completed
	if result[1] == 200:
		if expecting == "json":
			var data = JSON.parse_string(result[3].get_string_from_utf8())
			data["Ok"] = true
			return data
		elif expecting == "raw":
			return {"Ok": true, "data": result[1]}
	return {"Ok": false}
