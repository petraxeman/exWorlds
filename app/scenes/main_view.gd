extends Control

const tabs_dict: Dictionary = {
	"homepage": ["Home page", preload("res://scenes/main_view_tabs/home_page.tscn")]
}



func _ready():
	_render()
	create_tab("homepage")


func _render():
	ThemeHandler.current_theme.set_zone("main-view")
	ThemeHandler.current_theme.apply_theme(self)


func create_tab(tab_name: String) -> Node:
	if not (tab_name in tabs_dict.keys()):
		return Node.new()
	var new_tab: Array = tabs_dict[tab_name]
	var new_tab_scene = new_tab[1].instantiate()
	
	$vbox/tab_container.add_child(new_tab_scene)
	$vbox/top/tab_bar.add_tab(new_tab[0])
	$vbox/top/tab_bar.current_tab = $vbox/tab_container.get_children().size() - 1
	
	if new_tab_scene.has_signal("close_request"):
		new_tab_scene.close_request.connect(remove_tab_by_ref)
	return new_tab_scene


func remove_tab(tab: int) -> void:
	print("Pls close tab", tab)
	$vbox/top/tab_bar.remove_tab(tab)
	$vbox/tab_container.get_children()[tab].queue_free()


func remove_tab_by_ref(tab: Node) -> void:
	var index = $vbox/tab_container.get_children().find(tab)
	remove_tab(index)


func _on_tab_bar_tab_changed(tab):
	$vbox/tab_container.current_tab = tab


func _on_tab_bar_tab_close_pressed(tab):
	remove_tab(tab)


func _on_home_pressed():
	create_tab("home")


func _on_game_systems_pressed():
	create_tab("game_systems")
