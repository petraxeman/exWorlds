extends Node

var icons: Dictionary = {}

func _ready():
	icons["opened_book"] = load("res://assets/icons/bookmarklet.svg")
	icons["bow"] = load("res://assets/icons/bow-arrow.svg")
	icons["character"] = load("res://assets/icons/character.svg")
	icons["chest"] = load("res://assets/icons/chest.svg")
	icons["goblin_camp"] = load("res://assets/icons/goblin-camp.svg")
	icons["goblin_head"] = load("res://assets/icons/goblin-head.svg")
	icons["goblin"] = load("res://assets/icons/goblin.svg")
	icons["open_chest"] = load("res://assets/icons/open-chest.svg")
	icons["orc_head"] = load("res://assets/icons/orc-head.svg")
	icons["sword"] = load("res://assets/icons/piercing-sword.svg")
	icons["potion"] = load("res://assets/icons/potion-ball.svg")
	icons["scroll"] = load("res://assets/icons/scroll-unfurled.svg")
	icons["tied_scroll"] = load("res://assets/icons/tied-scroll.svg")


func get_icon(icon_name: String) -> Image:
	return icons[icon_name].get_image()


func get_icons() -> Array:
	return icons.keys()
