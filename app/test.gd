extends Node2D



func _ready():
	var luaapi: LuaAPI = LuaAPI.new()
	var code: String = "
	function add_some()
		return 1 + 2
	end
	"
	
	luaapi.do_string(code)
	print(luaapi.function_exists("add_some_"))
