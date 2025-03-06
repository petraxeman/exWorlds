extends Control

var previous_view


func _ready():
	Globals.current_theme.set_zone("settings-view")
	ExworldsTheme.apply_theme(self)

func _on_button_pressed():
	get_tree().root.add_child(previous_view)
	Globals.current_theme.set_zone("server-selection")
	queue_free()
