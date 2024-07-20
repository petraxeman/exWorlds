extends Control

const tabs_dict: Dictionary = {
	"home": ["Home page", preload("res://scenes/elements/home_tab.tscn")],
	"game_systems": ["Game systems", preload("res://scenes/elements/game_systems.tscn")],
	"create_new_system": ["Create new system", preload("res://scenes/elements/create_system.tscn")]
}



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	pass



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func create_tab(tab_name: String) -> void:
	if not (tab_name in tabs_dict.keys()):
		return
	var new_tab: Array = tabs_dict[tab_name]
	var new_tab_scene = new_tab[1].instantiate()
	$tab_container.add_child(new_tab_scene)
	$tab_bar.add_tab(new_tab[0])


func remove_tab(tab: int) -> void:
	$tab_bar.remove_tab(tab)
	$tab_container.get_children()[tab].queue_free()


func remove_tab_by_ref(tab: Node) -> void:
	var index = $tab_container.get_children().find(tab)
	remove_tab(index)



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _on_tab_bar_tab_changed(tab):
	$tab_container.current_tab = tab


func _on_tab_bar_tab_close_pressed(tab):
	remove_tab(tab)


func _on_home_pressed():
	create_tab("home")


func _on_game_systems_pressed():
	create_tab("game_systems")
