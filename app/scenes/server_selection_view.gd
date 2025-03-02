extends Control



func _ready():
	$content/actions/panel/margin/vbox/name/version.text = Globals.exworlds_version
	$background.texture = Globals.current_theme.get_resource_for("server-selection", "background")
	
	$content/actions/panel/margin/vbox/name/title.text = tr("EXWORLDS_TITLE")
	
	$content/actions/panel/margin/vbox/buttons/delete.text = tr("SERVER_SELECTION_DELETE")
	$content/actions/panel/margin/vbox/buttons/settings.text = tr("SERVER_SELECTION_SETTINGS")
	$content/actions/panel/margin/vbox/buttons/exit.text = tr("SERVER_SELECTION_EXIT")
	
	render_server_list()


func render_server_list():
	for child in $content/server_list/panel/maegin/scroll/server_list.get_children():
		child.queue_free()
	
	if not Globals.server_list:
		var lbl: Label = Label.new()
		lbl.text = tr("SERVER_SELECTION_NO_SERVERS")
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		$content/server_list/panel/maegin/scroll/server_list.add_child(lbl)
		$content/server_list/panel/maegin/scroll/server_list.alignment = BoxContainer.ALIGNMENT_CENTER
