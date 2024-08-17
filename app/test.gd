extends Node2D

var some_txt = "This is description of  #[@items#bow] tem in #[.name or   .codename] #[#sword] #[@items#axe.damage] #[@table#spike] and he has a description like #[$short-desc]"

var at = "Это #[.name; default \"Типа лол\"; 10 words] и его нельзя использовать совместно с #[#sword;as link]. У #[.name] урон равен = #[.damage]. А это короткое описание для Топора #[#axe.desc; as link; 10 words]"

func _ready():
	var result: String = await TextLib.format(at, {"game_system": "bonk-game-system", "table": "items", "note": "bow"})
	print(result)
