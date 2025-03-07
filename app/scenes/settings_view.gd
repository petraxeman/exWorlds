extends Control

var previous_view


func _ready():
	Globals.current_theme.set_zone("settings-view")
	ExworldsTheme.apply_theme(self)
	_render_text()
	_render_available_locales()
	_render_available_themes()


func _render_text():
	$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/label.text = tr("SETTINGS_VIEW_LOCALIZATION_LBL") + ": "
	$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/label.text = tr("SETTINGS_VIEW_THEME_LBL") + ": "


func _render_available_locales():
	$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.clear()
	var i: int = 0
	for loc in TranslationServer.get_loaded_locales():
		$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.add_item(loc)
		if loc == Globals.locale:
			$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.selected = i
		i += 1


func _render_available_themes():
	$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.clear()
	var i: int = 0
	for thm in Globals.loaded_themes:
		$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.add_item(thm.visible_name)
		$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.set_item_metadata(i, thm.codename)
		if thm.visible_name == Globals.current_theme.visible_name:
			$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.selected = i
		i += 1



func _on_cancel_and_exit_pressed():
	previous_view._render()
	get_tree().root.add_child(previous_view)
	Globals.current_theme.set_zone("server-selection")
	queue_free()


func _on_save_and_exit_pressed():
	# Locale setup
	var locale_idx = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.selected
	Globals.locale = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.get_item_text(locale_idx)
	var theme_idx = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.selected
	Globals.current_theme_codename = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.get_item_metadata(theme_idx)
	Globals._save_config()
	_on_cancel_and_exit_pressed()
