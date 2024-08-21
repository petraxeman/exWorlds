extends ScrollContainer

@onready var row_scene = preload("res://scenes/additional/library_additional/note_search_additional/row.tscn")



func render_notes(game_system: String, table_codename: String, notes: Array, fields: Array):
	for child in $content.get_children():
		child.queue_free()
	
	var context: Dictionary = {}
	for note in notes:
		var new_row = row_scene.instantiate()
		
		var rendering_note_data: Array = []
		var current_address: Dictionary = {"game_system": game_system, "table": table_codename, "note": note}
		
		for field in fields:
			var dict_field: Dictionary = TextLib.rel_to_abs(TextLib.convert_element_into_dict(field["codename"]), current_address)
			
			if dict_field["ref"] == "field":
				if not context.get("{0}:{1}".format([dict_field["table"], dict_field["note"]]), false):
					await update_context(context, dict_field, current_address)
				var context_note_data = context.get("{0}:{1}".format([dict_field["table"], dict_field["note"]]), {}).get(dict_field["field"], {})
				if not context_note_data is Dictionary:
					continue
				match context_note_data.get("type", "string"):
					"string", "paragraph":
						rendering_note_data.append(await TextLib.format(context_note_data.get("value", ""), current_address, context))
					"image":
						rendering_note_data.append(await ResLoader.get_image(context_note_data.get("value", "")))
					"number":
						if context_note_data.get("min", 0) == context_note_data.get("max", 0):
							rendering_note_data.append("{0}".format([str(context_note_data.get("min", 0))]))
						else:
							rendering_note_data.append("{0}-{1}".format([str(context_note_data.get("min", 0)), str(context_note_data.get("max", 0))]))
				
			elif dict_field["ref"] == "property":
				rendering_note_data.append(await TextLib.format("#[%s]"%field["codename"], current_address, context))
			
		new_row.build(note, rendering_note_data)
		$content.add_child(new_row)


func update_context(context: Dictionary, request: Dictionary, current_address: Dictionary):
	if not context.get("{0}:{1}".format([request["table"], request["note"]]), false):
		var response = await ResLoader.get_note(current_address["game_system"], request["table"], request["note"])
		response.erase("Ok")
		context["{0}:{1}".format([request["table"], request["note"]])] = response
	if not context.get("{0}:properties".format([request["table"]])):
		var req_table = await ResLoader.get_table(current_address["game_system"], request["table"])
		var properties: Dictionary = {}
		for property in req_table["table_data"]["properties"]:
			properties[property["codename"]] = property["value"]
		context["{0}:properties".format([request["table"]])] = properties
