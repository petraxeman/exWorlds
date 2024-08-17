extends VBoxContainer

signal page_changed(page_index: int)

var max_page: int = 10
var current_page: int = 1
var page_selection_focused: bool = false
var page_selector_node: SpinBox



func _ready():
	render()


func _input(event):
	if Input.is_action_pressed("Enter") and page_selection_focused:
		page_selector_node.apply()
		page_selection_focused = false
		_on_numeric_pressed(page_selector_node.value)


func set_page_count(count: int):
	max_page = count
	current_page = 1


func render():
	for child in $pages.get_children():
		child.queue_free()
	
	if max_page <= 1:
		return
	
	if max_page <= 6:
		render_short_bar()
	else:
		render_long_bar()


func render_short_bar():
	var prev_button: Button = Button.new()
	prev_button.disabled = current_page == 1
	prev_button.pressed.connect(_on_prev_pressed)
	prev_button.text = "<"
	$pages.add_child(prev_button)
	
	for i in range(max_page):
		var numeric_button: Button = Button.new()
		numeric_button.text = str(i + 1)
		numeric_button.disabled = i+1 == current_page
		numeric_button.pressed.connect(_on_numeric_pressed.bind(i+1))
		$pages.add_child(numeric_button)
	
	var next_button: Button = Button.new()
	next_button.disabled = current_page == max_page
	next_button.pressed.connect(_on_next_pressed)
	next_button.text = ">"
	$pages.add_child(next_button)


func render_long_bar():
	var prev_button: Button = Button.new()
	prev_button.disabled = current_page == 1
	prev_button.pressed.connect(_on_prev_pressed)
	prev_button.text = "<"
	$pages.add_child(prev_button)
	
	for i in range(current_page - 4, current_page - 1):
		if i+1 < 1:
			continue
		var numeric_button: Button = Button.new()
		numeric_button.text = str(i + 1)
		numeric_button.disabled = i+1 == current_page
		numeric_button.pressed.connect(_on_numeric_pressed.bind(i+1))
		$pages.add_child(numeric_button)
	
	var page_selector: SpinBox = SpinBox.new()
	page_selector.min_value = 1
	page_selector.max_value = max_page
	page_selector.get_line_edit().focus_entered.connect(_on_page_selection_focused)
	page_selector.get_line_edit().focus_exited.connect(_on_page_selection_unfocused)
	page_selector_node = page_selector
	page_selector.value = current_page
	$pages.add_child(page_selector)
	
	for i in range(current_page, current_page+3):
		if i+1 > max_page:
			continue
		var numeric_button: Button = Button.new()
		numeric_button.text = str(i + 1)
		numeric_button.disabled = i+1 == current_page
		numeric_button.pressed.connect(_on_numeric_pressed.bind(i+1))
		$pages.add_child(numeric_button)
	
	var next_button: Button = Button.new()
	next_button.disabled = current_page == max_page
	next_button.pressed.connect(_on_next_pressed)
	next_button.text = ">"
	$pages.add_child(next_button)


func _on_page_selection_focused():
	page_selection_focused = true


func _on_page_selection_unfocused():
	page_selection_focused = false


func _on_prev_pressed():
	if current_page == 1:
		return
	
	current_page -= 1
	render()
	emit_signal("page_changed", current_page)


func _on_next_pressed():
	if current_page == max_page:
		return
	
	current_page += 1
	render()
	emit_signal("page_changed", current_page)


func _on_numeric_pressed(page: int):
	if page < 1 or page > max_page:
		return
	
	current_page = page
	render()
	emit_signal("page_changed", current_page)
