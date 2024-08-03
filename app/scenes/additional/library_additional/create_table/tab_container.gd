extends VBoxContainer

signal change_tab
signal delete_tab



func _ready():
	size_flags_horizontal = Control.SIZE_EXPAND_FILL

func add_page(page_name: String) -> Node:
	var vbox: VBoxContainer = VBoxContainer.new()
	$tabbar.add_tab(page_name)
	$tabcontainer.add_child(vbox)
	return vbox


func _on_tabbar_tab_clicked(tab: int):
	$tabcontainer.current_tab = tab


func _on_settings_pressed():
	emit_signal("change_tab")


func _on_delete_pressed():
	emit_signal("delete_tab")
