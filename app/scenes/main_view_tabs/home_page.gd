extends Control

signal close_request



func _ready():
	var previous_zone = ThemeHandler.current_theme.active_zone
	ThemeHandler.current_theme.set_zone("main_view_homepage")
	ThemeHandler.current_theme.apply_theme(self)
	ThemeHandler.current_theme.set_zone(previous_zone)


func _on_exit_pressed():
	close_request.emit(self)
	print(close_request.get_connections())
