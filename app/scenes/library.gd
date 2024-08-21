extends Control

const tabs_dict: Dictionary = {
	"home": ["Home page", preload("res://scenes/additional/library_additional/home_tab.tscn")],
	"game_systems": ["Game systems", preload("res://scenes/additional/library_additional/game_systems.tscn")],
	"create_system": ["Create new system", preload("res://scenes/additional/library_additional/create_system.tscn")],
	"game_system": ["System view", preload("res://scenes/additional/library_additional/game_system.tscn")],
	"create_table": ["Create table", preload("res://scenes/additional/library_additional/create_table.tscn")],
	"create_note": ["Create note", preload("res://scenes/additional/library_additional/note_creation.tscn")],
	"note_viewer": ["View notes", preload("res://scenes/additional/library_additional/notes_search.tscn")]
}



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func create_tab(tab_name: String) -> Node:
	if not (tab_name in tabs_dict.keys()):
		return Node.new()
	var new_tab: Array = tabs_dict[tab_name]
	var new_tab_scene = new_tab[1].instantiate()
	$tab_container.add_child(new_tab_scene)
	$tab_bar.add_tab(new_tab[0])
	
	$tab_bar.current_tab = $tab_container.get_children().size() - 1
	return new_tab_scene


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
