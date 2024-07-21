extends Control

var parent: Node
var page: int = 1
var current_page: Array = []

# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	parent = get_node("/root/library")
	render_systems()



# ================================ #
# === USER CALLS AND FUNCTIONS === #
# ================================ #

func render_systems() -> void:
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



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _on_create_new_pressed():
	parent.create_tab("create_new_system")


func _on_refresh_pressed():
	render_systems()
