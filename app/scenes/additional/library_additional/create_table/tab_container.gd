extends VBoxContainer

signal change_tab
signal delete_tab

var can_be_changed: bool = true:
	set(value):
		if value == false:
			$tabbar/hbox/settings.hide()
			$tabbar/hbox/delete.hide()
		else:
			$tabbar/hbox/settings.show()
			$tabbar/hbox/delete.show()


func _ready():
	size_flags_horizontal = Control.SIZE_EXPAND_FILL


func add_page(page_name: String) -> Node:
	var margin: MarginContainer = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 10)
	margin.add_theme_constant_override("margin_right", 10)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	var vbox: VBoxContainer = VBoxContainer.new()
	margin.add_child(vbox)
	$tabbar.add_tab(page_name)
	$tabcontainer.add_child(margin)
	return vbox


func _on_tabbar_tab_clicked(tab: int):
	$tabcontainer.current_tab = tab


func _on_settings_pressed():
	emit_signal("change_tab")


func _on_delete_pressed():
	emit_signal("delete_tab")
