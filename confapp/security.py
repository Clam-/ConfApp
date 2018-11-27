from pyramid.security import unauthenticated_userid

from confapp.models import User, UserRole

def groupfinder(userid, request):
	user = User.get_by_username(userid)
	if user:
		return [user.role]


#request.effective_principals
def checkAdmin(effective_principals):
	return any(x in (UserRole.admin, UserRole.superadmin) for x in effective_principals)

def checkSport(effective_principals):
	return any(x in (UserRole.sports, UserRole.admin, UserRole.superadmin) for x in effective_principals)

def checkMain(effective_principals):
	return any(x in (UserRole.main, UserRole.admin, UserRole.superadmin) for x in effective_principals)
