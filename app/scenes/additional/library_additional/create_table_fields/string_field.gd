extends PanelContainer

var parent: Node

func _on_clone_pressed():
	parent.create_field(0)

func _on_delete_pressed():
	queue_free()
