extends Control

var del_index: int = -1
var ent_index: int = -1



func _ready():
	IP.resolve_hostname("localhost", IP.TYPE_IPV4)
	render_servers()

func _on_player_connected(id):
	print(id)

func _on_player_disconnected(id):
	print(id)
	
func render_servers():
	var server_row: PackedScene = load("res://scenes/elements/server_selection/server_row.tscn")
	for child in $margin/vbox/scroll/margin/vbox.get_children():
		child.queue_free()
	for i in range(Global.servers.size()):
		var server: Dictionary = Global.servers[i]
		var row_instance: HBoxContainer = server_row.instantiate()
		if server["can_del"]:
			row_instance.get_node("del").disabled = false
			row_instance.get_node("del").pressed.connect(_del_server_pressed.bind(i))
		row_instance.get_node("enter").pressed.connect(_enter_server_pressed.bind(i))
		row_instance.get_node("name").text = server["name"]
		row_instance.get_node("ip").text = "(" + server["address"] + ")"
		$margin/vbox/scroll/margin/vbox.add_child(row_instance)
		$margin/vbox/scroll/margin/vbox.add_child(HSeparator.new())


func get_info() -> Dictionary:
	var curr_server: Dictionary = Global.servers[ent_index]
	$HTTPRequest.request("http://" + curr_server["address"] + "/rlapi/get_info", [], HTTPClient.METHOD_POST)
	var result = await $HTTPRequest.request_completed
	if not result[1] == 200:
		return {"result": 0}
	return JSON.parse_string(result[3].get_string_from_utf8())


func login(username: String, password: String) -> bool:
	var curr_server: Dictionary = Global.servers[ent_index]
	var headers: Array = ["user-login:" + username, "user-password:" + password]
	$HTTPRequest.request("http://" + curr_server["address"] + "/auth", headers, HTTPClient.METHOD_POST)
	var result = await $HTTPRequest.request_completed
	if not result[1] == 200:
		return false
	
	var data = JSON.parse_string(result[3].get_string_from_utf8())
	if data["result"] == 1:
		Global.active_server = ent_index
		Global.servers[ent_index]["token"] = data["token"]
		Global.servers[ent_index]["token_ttl"] = Time.get_unix_time_from_system() + data["ttl"]
		return true
	else:
		return false


func register(username: String, password: String) -> bool:
	var curr_server: Dictionary = Global.servers[ent_index]
	var headers: Array = ["user-login:" + username, "user-password:" + password]
	$HTTPRequest.request("http://" + curr_server["address"] + "/register", headers, HTTPClient.METHOD_POST)
	var result = await $HTTPRequest.request_completed
	if not result[1] == 200:
		return false
	
	var data = JSON.parse_string(result[3].get_string_from_utf8())
	if data["result"] == 1:
		return true
	else:
		return false


# === CATCHING SIGNALS === #

func _add_server_pressed():
	var server_address: String = $margin/vbox/add_new/ip.get_text()
	var server_name: String = $margin/vbox/add_new/name.get_text()
	Global.add_server(server_name, server_address)
	render_servers()


func _del_server_pressed(i):
	$del_confirm_window/vbox/label.text = "Are you sure?\nYou want to delete server:\n\"" + Global.servers[i]["name"] + "\""
	$del_confirm_window.show()
	del_index = i
	render_servers()
	

func _enter_server_pressed(i):
	ent_index = i
	$auth_rect.show()


func _del_confirm_pressed():
	if del_index > 0:
		Global.remove_server(del_index)
		render_servers()
	$del_confirm_window.hide()


func _del_cancel_pressed():
	$del_confirm_window.hide()


func _login_pressed():
	var username: String = $auth_rect/auth_window/vbox/margin/vbox/login.get_text()
	var password: String = $auth_rect/auth_window/vbox/margin/vbox/password.get_text()
	$auth_rect.hide()
	$waiting.show()
	$waiting/vbox/hello.text = "Hello " + username # 🔥
	$waiting/vbox/server.text = "Server: 🤔"
	$waiting/vbox/state.text = "Get information"
	var info: Dictionary = await get_info()
	if info["result"] == 1:
		$waiting/vbox/server.text = "Server: " + info["server_name"]
		$waiting/vbox/progress.value = 1
	$waiting/vbox/state.text = "Try login"
	var result: bool = await login(username, password)
	if not result:
		$waiting/vbox/state.text = "Failed. Try reg."
		result = await register(username, password)
		$waiting/vbox/progress.value = 2
		if not result:
			$waiting/vbox/state.text = "Failed. Wrong login or pass"
			$waiting/vbox/progress.value = 0
			return
		result = await login(username, password)
		$waiting/vbox/progress.value = 3
	
	if result:
		$waiting/vbox/progress.value = 4
		$waiting/vbox/state.text = "Now you will be redirected"
	$waiting.hide()
	#
	# SOME CODE TO REDIRECT WINDOW
	#


func _auth_completed(result: int, response_code: int, headers:  PackedStringArray, body: PackedByteArray):
	print(result)
	print(response_code)
	print(headers)
	print(body)


func _cancel_enter_pressed():
	$auth_rect.hide()
