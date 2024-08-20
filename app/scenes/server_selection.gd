extends Control

var sel_index: int = -1



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	render_servers()



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func render_servers():
	var server_row: PackedScene = load("res://scenes/additional/server_selector_additional/server_row.tscn")
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



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _add_server_pressed():
	var server_address: String = $margin/vbox/add_new/ip.get_text()
	var server_name: String = $margin/vbox/add_new/name.get_text()
	Global.add_server(server_name, server_address)
	render_servers()


# == Delition server from list == #

func _del_server_pressed(i):
	$del_confirm_window/vbox/label.text = "Are you sure?\nYou want to delete server:\n\"" + Global.servers[i]["name"] + "\""
	$del_confirm_window.show()
	sel_index = i


func _del_confirm_pressed():
	if sel_index >= 0:
		Global.remove_server(sel_index)
		render_servers()
	$del_confirm_window.hide()


func _del_cancel_pressed():
	$del_confirm_window.hide()

# =============================== #

# == Auth to server and enter == #

func _enter_server_pressed(i):
	sel_index = i
	var result = Global.set_active_server(i)
	if not result:
		return
	$auth_rect.show()


func _login_pressed():
	var username: String = $auth_rect/auth_window/vbox/margin/vbox/login.get_text()
	var password: String = $auth_rect/auth_window/vbox/margin/vbox/password.get_text()
	__init_server_enter_view(username)
	var info: Dictionary = await ResLoader.get_info()
	if info.get("error", false): __exit_from_enter_view(); return
	__set_server_info(info)
	var result: bool = await Global.auth(username, password)
	#if not result:
	#	$waiting/vbox/state.text = "Failed. Try reg."
	#	result = await Global.register(username, password)
	$waiting/vbox/progress.value = 2
	if not result:
		$waiting/vbox/state.text = "Failed. Wrong login or pass"
		$waiting/vbox/progress.value = 0
		__exit_from_enter_view()
		return
	result = await Global.auth(username, password)
	$waiting/vbox/progress.value = 3
	
	if result:
		$waiting/vbox/progress.value = 4
		$waiting/vbox/state.text = "Now you will be redirected"
	$waiting.hide()
	
	#Global.cache = CacheLib.init_cache_db(Global.active_server["address"])
	var library_scene: PackedScene = preload("res://scenes/library.tscn")
	get_tree().root.add_child(library_scene.instantiate())
	get_node("/root/server_selection").free()
	


func __init_server_enter_view(username: String) -> void:
	$auth_rect.hide()
	$waiting.show()
	$waiting/vbox/hello.text = "Hello " + username # 🔥
	$waiting/vbox/server.text = "Server: 🤔"
	$waiting/vbox/state.text = "Get information"

func __set_server_info(info: Dictionary) -> void:
	$waiting/vbox/server.text = "Server: " + info["server_name"]
	$waiting/vbox/progress.value = 1
	$waiting/vbox/state.text = "Try login"

func __exit_from_enter_view() -> void:
	$waiting.hide()


func _cancel_enter_pressed():
	$auth_rect.hide()

# ============================== #
