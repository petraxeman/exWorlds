extends Node
class_name UrlEnum

const endpoints: Dictionary = {
	"auth": "/account/auth",
	"registration": "/account/registration",
	"server_info": "/server/info",
	"put_image": "/images/upload",
	"info_image": "/images/info",
	"download_image": "/images/download",
	"create_game_system": "/structs/create/system"
}



static func build(proto: String, url: String, endpoint: String):
	return proto + "://" + url + endpoints[endpoint]
