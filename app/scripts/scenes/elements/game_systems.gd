extends Control

var parent: Node
var page: int = 1
var max_page: int
var current_page: Array = []
var rendering_page: bool = true


# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	parent = get_node("/root/library")
	render_systems()
	render_pages()



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func render_systems() -> void:
	rendering_page = true
	$vbox/margin/hbox/refresh.disabled = true
	for child in $vbox/margin2/scroll/vbox/game_systems_list.get_children():
		child.queue_free()
	var systems: Array = await ResLoader.get_systems(page - 1)
	for system in systems:
		var system_card = preload("res://scenes/elements/game_system_card.tscn").instantiate()
		system_card.get_node("refrect/texture").texture = ImageTexture.create_from_image(system["image"]["image"])
		system_card.get_node("refrect/panel/texts/system_name").text = system["name"]
		system_card.get_node("refrect/panel/texts/author").text = system["author"]
		if not system["can_change"]:
			system_card.get_node("hbox/edit").hide()
		$vbox/margin2/scroll/vbox/game_systems_list.add_child(system_card)
	$vbox/margin/hbox/refresh.disabled = false
	rendering_page = false


func render_pages() -> void:
	var systems_count: int = await ResLoader.get_systems_count()
	var buttons_count: int = ceil(systems_count / 10.0)
	if buttons_count <= 1:
		return
	var left_button: Button = Button.new()
	left_button.add_theme_font_size_override("25", 25)
	left_button.text = "◀"
	left_button.pressed.connect(_on_previous_page_pressed)
	$vbox/margin3/pages.add_child(left_button)
	for i in range(buttons_count):
		var page_button: Button = Button.new()
		page_button.add_theme_font_size_override("25", 25)
		page_button.text = str(i+1)
		page_button.pressed.connect(_on_page_changed.bind(i+1))
		$vbox/margin3/pages.add_child(page_button)
	var right_button: Button = Button.new()
	right_button.add_theme_font_size_override("25", 25)
	right_button.text = "▶"
	right_button.pressed.connect(_on_next_page_pressed)
	$vbox/margin3/pages.add_child(right_button)
	$vbox/margin3/pages.get_children()[1].disabled = true
	max_page = $vbox/margin3/pages.get_children().size() - 2



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _on_create_new_pressed():
	parent.create_tab("create_new_system")


func _on_refresh_pressed():
	render_systems()


func _chech_page_buttons():
	if page == 1:
		$vbox/margin3/pages.get_children()[0].disabled = true
	else:
		$vbox/margin3/pages.get_children()[0].disabled = false
	if page == max_page:
		$vbox/margin3/pages.get_children()[-1].disabled = true
	else:
		$vbox/margin3/pages.get_children()[-1].disabled = false


func _on_previous_page_pressed():
	if rendering_page: return
	if page - 1 < 1: return
	$vbox/margin3/pages.get_children()[page].disabled = false
	$vbox/margin3/pages.get_children()[page - 1].disabled = true
	page = page - 1
	_chech_page_buttons()
	render_systems()


func _on_next_page_pressed():
	if rendering_page: return
	if page + 1 > max_page: return
	$vbox/margin3/pages.get_children()[page].disabled = false
	$vbox/margin3/pages.get_children()[page + 1].disabled = true
	page = page + 1
	_chech_page_buttons()
	render_systems()


func _on_page_changed(page_number: int):
	if rendering_page: return
	$vbox/margin3/pages.get_children()[page].disabled = false
	$vbox/margin3/pages.get_children()[page_number].disabled = true
	page = page_number
	_chech_page_buttons()
	render_systems()
