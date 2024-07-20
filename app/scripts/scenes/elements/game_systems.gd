extends Control

var parent: Node



# ================================== #
# === SYSTEM CALLS AND FUNCTIONS === #
# ================================== #

func _ready():
	parent = get_node("/root/library")



# ====================================== #
# === ADDITIONAL CALLS AND FUNCTIONS === #
# ====================================== #

func _on_create_new_pressed():
	parent.create_tab("create_new_system")
