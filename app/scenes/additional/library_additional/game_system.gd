extends Control

var game_system_codename: String
var rendering_categories: bool = false
var can_change: bool = false
@onready var parent: Node = get_node("/root/library")




func setup_view(system_name: String, system_codename: String, author: String, notes_count: int, image: ImageTexture):
	game_system_codename = system_codename
	$vbox/margin/hbox/names/names/system_name.text = system_name
	$vbox/margin/hbox/names/names/code_name.text = "(%s)" % system_codename
	$vbox/margin/hbox/names/author.text = author
	$vbox/margin/hbox/names/content_count.text = "Notes: %d" % notes_count
	$vbox/margin/hbox/refrect/texture.texture = image
	
	$delete_popup/margin/vbox/label.text = "You want to remove \"{0}\" system.\nWrite \"{0}\" in the field below.".format([game_system_codename])
	$delete_popup/margin/vbox/lineedit.placeholder_text = game_system_codename
	
	if author != Global.get_current_user()["username"]:
		$vbox/margin/hbox/variants/delete.hide()
		$vbox/margin/hbox/variants/create_new_table.hide()
	else:
		can_change = true
	
	render_categories()


func render_categories():
	if rendering_categories: return
	for child in $vbox/scroll/grid.get_children():
		child.queue_free()
	$vbox/margin/hbox/variants/refresh.disabled = true
	rendering_categories = true
	var categories = await ResLoader.get_tables(game_system_codename)
	for category in categories:
		var category_button = preload("res://scenes/additional/library_additional/game_system_additional/table_selector_button.tscn").instantiate()
		category_button.set_icon(category["icon"])
		category_button.set_label(category["name"])
		category_button.table_codename = category["codename"]
		category_button.game_system = game_system_codename
		category_button.game_system_view = self
		
		if not can_change:
			category_button.disable_changment()
		$vbox/scroll/grid.add_child(category_button)
	$vbox/margin/hbox/variants/refresh.disabled = false
	rendering_categories = false


func _on_refresh_pressed():
	render_categories()


func _on_create_new_table_pressed():
	var create_table_scene: Node = parent.create_tab("create_table")
	create_table_scene.game_system = game_system_codename
	create_table_scene.render_table()


func _on_cancel_system_delition_pressed():
	$delete_popup.hide()


func _on_ok_system_delition_pressed():
	if game_system_codename == $delete_popup/margin/vbox/lineedit.text:
		ResLoader.delete_system(game_system_codename)
	parent.remove_tab_by_ref(self)


func _on_start_delete_pressed():
	$delete_popup.show()
