extends Control

var game_system_codename: String
var rendering_categories: bool = false
var parent: Node



func _ready():
	parent = get_node("/root/library")

func setup_view(system_name: String, system_codename: String, author: String, notes_count: int, image: ImageTexture):
	game_system_codename = system_codename
	$vbox/margin/hbox/names/names/system_name.text = system_name
	$vbox/margin/hbox/names/names/code_name.text = "(%s)" % system_codename
	$vbox/margin/hbox/names/author.text = author
	$vbox/margin/hbox/names/content_count.text = "Notes: %d" % notes_count
	$vbox/margin/hbox/refrect/texture.texture = image
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
		$vbox/scroll/grid.add_child(category_button)
	$vbox/margin/hbox/variants/refresh.disabled = false
	rendering_categories = false


func _on_refresh_pressed():
	render_categories()


func _on_create_new_table_pressed():
	parent.create_tab("create_table")
