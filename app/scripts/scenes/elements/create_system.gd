extends Control

var image: Image

func _ready():
	pass


func create_new_system(sname: String, cname: String, image: PackedByteArray) -> bool:
	var http: HTTPRequest = $HTTPRequest#HTTPRequest.new()
	#var headers: Array = ["token:" + Global.servers[Global.active_server]["token"]]
	var headers = ["content:111"]
	var url = "http://127.0.0.1:5000/capi/create_system"
	#var url: String = "http://" + Global.servers[Global.active_server]["address"] + create_system_afex
	var data = {"name": sname, "code_name": cname, "image": Marshalls.raw_to_base64(image)}
	http.request(url, headers, HTTPClient.METHOD_POST, str(data))
	await http.request_completed
	print("Sended")
	return false


func _on_select_file_pressed():
	$FileDialog.show()
	

func _on_create_system_pressed():
	if not image:
		image = Image.load_from_file("res://assets/Age_of_Ashes_1_-_Hellknight_Hill (1)-2.png")
	await create_new_system($vbox/game_system_name.text, $vbox/game_system_code_name.text, image.get_data())
	
	var tab_container: TabContainer = self.get_parent()
	var tab_bar: TabBar = self.get_parent().get_parent().get_node("tab_bar")
	var index = tab_container.get_children().find(self)
	tab_bar.remove_tab(index)
	self.queue_free()


func _on_file_dialog_file_selected(path):
	$vbox/file_chose/label.text = path
	image = Image.load_from_file(path)
	$vbox/refrect/texture.texture = ImageTexture.create_from_image(image)
