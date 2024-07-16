extends Control

@onready var home_tab = preload("res://scenes/elements/home_tab.tscn")
@onready var game_systems_tab = preload("res://scenes/elements/game_systems_tab.tscn")
@onready var create_new_system_tab = preload("res://scenes/elements/create_system.tscn")

func _ready():
	pass


func add_create_new_system_tab():
	$tab_bar.add_tab("Game systems")
	$tab_container.add_child(create_new_system_tab.instantiate())
	
# ======================== #
# === CATCHING SIGNALS === #
# ======================== #

func _on_tab_bar_tab_changed(tab):
	$tab_container.current_tab = tab


func _on_tab_bar_tab_close_pressed(tab):
	$tab_bar.remove_tab(tab)
	$tab_container.get_children()[tab].queue_free()
	TabContainer


func _on_home_pressed():
	$tab_bar.add_tab("Home tab")
	$tab_container.add_child(home_tab.instantiate())


func _on_game_systems_pressed():
	$tab_bar.add_tab("Game systems")
	$tab_container.add_child(game_systems_tab.instantiate())
