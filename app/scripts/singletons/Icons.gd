extends Node

var icons: Dictionary = {}

func _ready():
	icons["opened_book"] = Image.load_from_file("res://assets/icons/bookmarklet.svg")
	icons["bow"] = Image.load_from_file("res://assets/icons/bow-arrow.svg")
	icons["character"] = Image.load_from_file("res://assets/icons/character.svg")
	icons["chest"] = Image.load_from_file("res://assets/icons/chest.svg")
	icons["goblin_camp"] = Image.load_from_file("res://assets/icons/goblin-camp.svg")
	icons["goblin_head"] = Image.load_from_file("res://assets/icons/goblin-head.svg")
	icons["goblin"] = Image.load_from_file("res://assets/icons/goblin.svg")
	icons["open_chest"] = Image.load_from_file("res://assets/icons/open-chest.svg")
	icons["orc_head"] = Image.load_from_file("res://assets/icons/orc-head.svg")
	icons["sword"] = Image.load_from_file("res://assets/icons/piercing-sword.svg")
	icons["potion"] = Image.load_from_file("res://assets/icons/potion-ball.svg")
	icons["scroll"] = Image.load_from_file("res://assets/icons/scroll-unfurled.svg")
	icons["tied_scroll"] = Image.load_from_file("res://assets/icons/tied-scroll.svg")


func get_icon(icon_name: String) -> Image:
	return icons[icon_name]
