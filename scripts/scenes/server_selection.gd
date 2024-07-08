extends Control

var del_index: int = -1
var ent_index: int = -1


func _ready():
	render_servers()

func render_servers():
	var server_row: PackedScene = load("res://scenes/elements/server_selection/server_row.tscn")
	for child in $margin/vbox/scroll/margin/vbox.get_children():
		child.queue_free()
	for i in range(Global.servers.size()):
		var server: Dictionary = Global.servers[i]
		var row_instance: HBoxContainer = server_row.instantiate()
		if server["can_del"]:
			row_instance.get_node("del").disabled = false
			row_instance.get_node("del").pressed.connect(func(x=i): _del_server_pressed(i))
			row_instance.get_node("enter").pressed.connect(func(x=i): _enter_server_pressed(i))
		row_instance.get_node("name").text = server["name"]
		row_instance.get_node("ip").text = "(" + server["address"] + ")"
		$margin/vbox/scroll/margin/vbox.add_child(row_instance)
		$margin/vbox/scroll/margin/vbox.add_child(HSeparator.new())

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
	$auth_window.show()


func _del_confirm_pressed():
	if del_index > 0:
		Global.remove_server(del_index)
		render_servers()
	$del_confirm_window.hide()


func _del_cancel_pressed():
	$del_confirm_window.hide()


func _login_pressed():
	print("Login is: \"" + $auth_window/vbox/margin/vbox/login.get_text() + "\"")
	print("Password is is: \"" + $auth_window/vbox/margin/vbox/password.get_text() + "\"")


func _cancel_enter_pressed():
	$auth_window.hide()
