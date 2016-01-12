# pass, group
USERS = {
	'main' : 'mainpass',
	'sport' : 'sportpass',
	'admin' : 'adminpass',
}
GROUPS = {
	'main' : ['group:checkin'],
	'sport' : ['group:checkin'],
	'admin' : ['group:admin'],
}

def groupfinder(userid, request):
	if userid in USERS:
		return GROUPS.get(userid, [])
