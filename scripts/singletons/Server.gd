extends Node

var server_started: bool = false
var users: Dictionary = {}



func _ready():
	multiplayer.peer_connected.connect(_user_connected)
	multiplayer.peer_disconnected.connect(_user_disconnected)
	multiplayer.connected_to_server.connect(_user_connected.bind(-1))
	multiplayer.server_disconnected.connect(_user_disconnected.bind(-1))


func start(port: int):
	var peer = WebSocketMultiplayerPeer.new()
	var error = peer.create_server(port)
	if error: return error
	multiplayer.multiplayer_peer = peer
	server_started = true

func stop():
	server_started = false
	multiplayer.multiplayer_peer = null


# === SERVER CALLS === #
@rpc("any_peer", "call_local", "reliable")
func auth(login: String, password: String):
	# SOME LOGIC
	var id = multiplayer.get_unique_id()
	users[id]["login"] = login
	users[id]["password"] = password
	users[id]["auth"] = true


# === SIGNALS === #
func _user_connected(id):
	if id == -1:
		id = multiplayer.get_unique_id()
	users[id] = {"auth": false}

func _user_disconnected(id):
	if id == -1:
		id = multiplayer.get_unique_id()
	users.erase(id)
