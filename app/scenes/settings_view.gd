extends Control

var settings_view: PackedScene = load("res://scenes/server_selection_view.tscn")



func _ready():
	ThemeHandler.current_theme.set_zone("settings-view")
	ThemeHandler.current_theme.apply_theme(self)
	$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/file_picker.files_processed.connect(_update_themes_list)
	var localization_option_popup: PopupMenu = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.get_popup()
	localization_option_popup.set_meta("extheme_class", "localization-option-popup")
	localization_option_popup.transparent = true
	ThemeHandler.current_theme.apply_theme(localization_option_popup)
	
	var theme_option_popup: PopupMenu = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.get_popup()
	theme_option_popup.set_meta("extheme_class", "theme-option-popup")
	theme_option_popup.transparent = true
	ThemeHandler.current_theme.apply_theme(theme_option_popup)
	
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
	for t in ThemeHandler.finded_themes.values():
		$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.add_item(t.get("visible-name"))
		$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.set_item_metadata(i, t.get("codename"))
		if t.get("codename") == ThemeHandler.current_theme.codename:
			$settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.selected = i
		i += 1


func _update_themes_list():
	ThemeHandler._find_themes()
	_render_available_themes()


func _on_cancel_and_exit_pressed():
	var settings_instance = settings_view.instantiate()
	get_tree().root.add_child(settings_instance)
	queue_free()


func _on_save_and_exit_pressed():
	# Locale setup
	var locale_idx = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.selected
	Globals.locale = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/localization/option.get_item_text(locale_idx)
	var theme_idx = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.selected
	var theme_codename = $settings/vbox/margin/scroll/vbox/base_settings/margin/vbox/theme/option.get_item_metadata(theme_idx)
	ThemeHandler.set_theme(theme_codename)
	Globals._save_config()
	_on_cancel_and_exit_pressed()
