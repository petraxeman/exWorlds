extends Node

var get_formating_rows_regex: RegEx = RegEx.new()
var split_note_path: RegEx = RegEx.new()

var default_arg_parser: RegEx = RegEx.new()
var words_arg_parser: RegEx = RegEx.new()



func _ready():
	get_formating_rows_regex.compile(r"#\[(?<content>.[^\]]+)\]")
	split_note_path.compile(r"(?:@(?<table>[0-9a-z\-_]+))?(?:#(?<note>[0-9a-z\-_]+))?(?:(?:\.(?<field>[0-9a-z\-_]+))|(?:\$(?<property>[0-9a-z\-_]+))?)")
	
	default_arg_parser.compile(r"default \"(.*)\"")
	words_arg_parser.compile(r"([0-9]+) words")


func format(text: String, current_address: Dictionary, context: Dictionary = {}, path: Array = []) -> String:
	await update_context(context, text, current_address)
	var formated_text: String = text
	for row in get_formating_rows_regex.search_all(text):
		var elements: Array = row.get_string("content").split(" or ", false)
		var element_text: String = ""
		var dict_el: Dictionary
		
		for element in elements:
			dict_el = convert_element_into_dict(element)
			var table: String = current_address["table"] if dict_el["table"] == "table" else dict_el["table"]
			var note: String = current_address["note"] if dict_el["note"] == "note" else dict_el["note"]
			
			if not context.get("{0}:{1}".format([table, note]), false):
				continue
			
			var element_string: String
			if dict_el["ref"] == "field":
				element_string = str(context.get("{0}:{1}".format([table, note]), {}).get(dict_el["field"], ""))
			else:
				if str(context.get("{0}:{1}".format([table, note]), {}).get(dict_el["field"], "")) != "":
					element_string = str(context.get("{0}:{1}".format([table, note]), {}).get(dict_el["field"], ""))
				else:
					element_string = str(context.get(table+":properties", {}).get(dict_el["field"], ""))
			
			if current_address in path:
				element_text = element_string
				continue
			
			var element_address: Dictionary = current_address.duplicate(true)
			element_address["talbe"] = table
			element_address["note"] = note
			var element_path: Array = path.duplicate(true)
			element_path.append(current_address)
			
			#if dict_el["ref"] == "field":
			element_string = await format(element_string, element_address, context, element_path)
				
			if element_string != "":
				context["{0}:{1}".format([table, note])][dict_el["field"]] = element_string
				element_text = element_string
				break
		
		var raw_args: Array = row.get_string("content").split(";")
		var args: Dictionary = {}
		if raw_args.size() > 1:
			for arg in raw_args.slice(1):
				arg = arg.strip_edges(true, true)
				if "default" in arg:
					var default_parser_match = default_arg_parser.search(arg)
					args["default"] = default_parser_match.strings[1]
				elif "words" in arg:
					var words_parser_match = words_arg_parser.search(arg)
					var a: String = ""
					if words_parser_match.strings[1].is_valid_int():
						args["words"] = int(words_parser_match.strings[1])
				elif "as link" == arg:
					args["as link"] = true
		
		if "default" in args.keys() and element_text == "":
			element_text = args["default"]
		if "words" in args.keys():
			var words: Array = element_text.split(" ")
			element_text = " ".join(PackedStringArray(words.slice(0, args["words"])))
		if "as link" in args.keys():
			var abs_dict_el = rel_to_abs(dict_el, current_address)
			var link: String = "open_note/{0}/{1}/{2}".format([current_address["game_system"], abs_dict_el["table"], abs_dict_el["note"]])
			element_text = "[url={0}]{1}[/url]".format([link, element_text])
		formated_text = formated_text.replace(row.strings[0], element_text)
	print(context, "\n\n\n")
	return formated_text


func update_context(context: Dictionary, text: String, current_address: Dictionary):
	for row in get_formating_rows_regex.search_all(text):
		var elements: Array = row.get_string("content").split(" or ", false)
		for element in elements:
			var dict_el: Dictionary = convert_element_into_dict(element)
			var table: String = current_address["table"] if dict_el["table"] == "table" else dict_el["table"]
			var note: String = current_address["note"] if dict_el["note"] == "note" else dict_el["note"]
			
			if "{0}:{1}".format([table, note]) in context.keys():
				continue
			
			if dict_el.get("ref", "field") == "property" and (not table in context.keys()):
				var req_table = await ResLoader.get_table(current_address["game_system"], table)
				var properties: Dictionary = {}
				for property in req_table["properties"]:
					properties[property["codename"]] = property["value"]
				context[table+":properties"] = properties
				pass
				
			var req_note = await ResLoader.get_note(current_address["game_system"], table, note)
			req_note.erase("Ok")
			context["{0}:{1}".format([table, note])] = req_note


func rel_to_abs(element: Dictionary, current_address: Dictionary) -> Dictionary:
	var abs_element: Dictionary = element.duplicate(true)
	abs_element["table"] = abs_element["table"] if abs_element["table"] != "table" else current_address["table"]
	abs_element["note"] = abs_element["note"] if abs_element["note"] != "note" else current_address["note"]
	return abs_element


func convert_element_into_dict(element: String) -> Dictionary:
	var splited_element: RegExMatch = split_note_path.search(element)
	var dict_el: Dictionary = {}
	
	dict_el["table"] = "table" if splited_element.get_string("table") == "" else splited_element.get_string("table")
	dict_el["note"] = "note" if splited_element.get_string("note") == "" else splited_element.get_string("note")
	if splited_element.get_string("property") != "":
		dict_el["field"] = splited_element.get_string("property")
		dict_el["ref"] = "property"
	else:
		dict_el["field"] =  "name" if splited_element.get_string("field") == "" else splited_element.get_string("field")
		dict_el["ref"] = "field"
	
	return dict_el
