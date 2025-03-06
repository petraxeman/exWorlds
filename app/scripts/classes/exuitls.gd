extends Node
class_name EXUtils



static func array_to_color(arr: Array) -> Color:
	if arr.size() == 3:
		return Color(arr[0], arr[1], arr[2])
	elif arr.size() == 4:
		return Color(arr[0], arr[1], arr[2], arr[3])
	return Color(0, 0, 0)


static func disconnect_all(node: Node):
	for conn in node.get_incoming_connections():
		node.disconnect(conn["signal"], conn["callable"])


static func disconnect_all_pressed(node: Button):
	for conn in node.pressed.get_connections():
		node.pressed.disconnect(conn["callable"])
