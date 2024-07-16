extends Control



func _on_create_new_pressed():
	var parent = self.get_parent().get_parent()
	parent.add_create_new_system_tab()
