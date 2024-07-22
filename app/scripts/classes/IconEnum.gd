extends Node
class_name IconEnum

static var icons: Dictionary = {
	"opened_book": Image.load_from_file("res://assets/icons/bookmarklet.svg"),
	"bow": Image.load_from_file("res://assets/icons/bow-arrow.svg"),
	"character": Image.load_from_file("res://assets/icons/character.svg"),
	"chest": Image.load_from_file("res://assets/icons/chest.svg"),
	"goblin_camp": Image.load_from_file("res://assets/icons/goblin-camp.svg"),
	"goblin_head": Image.load_from_file("res://assets/icons/goblin-head.svg"),
	"goblin": Image.load_from_file("res://assets/icons/goblin.svg"),
	"open_chest": Image.load_from_file("res://assets/icons/open-chest.svg"),
	"orc_head": Image.load_from_file("res://assets/icons/orc-head.svg"),
	"sword": Image.load_from_file("res://assets/icons/piercing-sword.svg"),
	"potion": Image.load_from_file("res://assets/icons/potion-ball.svg"),
	"scroll": Image.load_from_file("res://assets/icons/scroll-unfurled.svg"),
	"tied_scroll": Image.load_from_file("res://assets/icons/tied-scroll.svg"),
}


static func get_image_texture(icon_name: String) -> ImageTexture:
	return ImageTexture.create_from_image(icons[icon_name])


static func get_image(icon_name: String) -> ImageTexture:
	return icons[icon_name]

