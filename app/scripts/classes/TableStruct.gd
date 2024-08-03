extends Node

var table: Dictionary

var tt = [
	[{"type": "string", "codename": "item-name", "name": "Item name"}],
	[
		{"type": "string", "codename": "item-damage", "name": "Item damage"},
		{"type": "string", "codename": "item-hp", "name": "Item hp"}
	],
	[
		{"block": true, "rows": [
			[{"type": "string", "codename": "str-mod", "name": "Strength mod"}],
			[
				{"type": "string", "codename": "str-plus", "name": "Strength +"},
				{"type": "string", "codename": "str-minus", "name": "Strength -"}
			]
		]},
		{"type": "string", "codename": "str-label", "name": "Strength label"}
	]
]

func _init():
	pass

