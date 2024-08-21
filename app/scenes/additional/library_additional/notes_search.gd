extends Control

@onready var list_view = preload("res://scenes/additional/library_additional/note_search_additional/row_content.tscn")

var table: Dictionary
var game_system: String
var table_codename: String
var current_view: Node = null
var current_fields: Array = []
var active_filter: Dictionary = {"text": "", "fields": {}}


func setup(gs: String, tc: String):
	$margin/vbox/pages.page_changed.connect(_on_page_changed)
	game_system = gs
	table_codename = tc
	table = await ResLoader.get_table(gs, tc)
	$filters.render_fields(table.get("search_fields", ""), table.get("table_fields"))
	$filters.filters_applied.connect(_on_filters_applied_pressed)
	check_page_count()
	render()


func render():
	$margin/vbox/pages.disable()
	current_fields = []
	if current_view:
		current_view.queue_free()
	if table["table_data"]["common"]["table_view"] == "List":
		$margin/vbox/view/columns.show()
		for label in $margin/vbox/view/columns/columns.get_children():
			label.queue_free()
		for field in table["table_data"]["common"]["short_view"].split(";"):
			field = field.strip_edges(true, true)
			var settings: Array = field.split(":")
			var label: Label = Label.new()
			label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			if settings.size() > 1:
				label.text = settings[1]
				current_fields.append({"codename": settings[0], "name": settings[1]})
			else:
				label.text = settings[0]
				current_fields.append({"codename": settings[0], "name": settings[0]})
			$margin/vbox/view/columns/columns.add_child(label)
		current_view = list_view.instantiate()
		$margin/vbox/view.add_child(current_view)
		await render_list()
	else:
		pass
	$margin/vbox/pages.enable()


func check_page_count():
	var response: Dictionary = await ResLoader.get_notes_count(game_system, table_codename, $margin/vbox/pages.current_page, active_filter)
	if response["Ok"]:
		$margin/vbox/pages.set_page_count(response.get("count", 1))


func render_list():
	$margin/vbox/pages.disable()
	var notes = await ResLoader.get_notes(game_system, table_codename, $margin/vbox/pages.current_page, active_filter)
	await current_view.render_notes(game_system, table_codename, notes.get("notes", []), current_fields)
	$margin/vbox/pages.enable()


func _on_page_changed(_page: int):
	await render_list()


func _on_fitlers_pressed():
	$filters.show()


func _on_search_pressed():
	active_filter = {"text": $margin/vbox/search/search_request.text, "fields": $filters.get_filter()}
	await check_page_count()
	await render()


func _on_filters_applied_pressed() :
	$margin/vbox/search/fitlers.text = "Filters ({0})".format([$filters.get_filter().size()])
