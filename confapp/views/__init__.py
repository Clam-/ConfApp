from logging import getLogger
log = getLogger(__name__)

from traceback import format_exc

from datetime import datetime
from pyramid.httpexceptions import (
	HTTPFound,
	HTTPNotFound,
	)

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from confapp.models import (
	DBSession,
	User,
	)

from paginate_sqlalchemy import SqlalchemyOrmPage

from pyramid.security import (
    remember,
    forget,
    )

from pyramid.view import (
	view_config,
	forbidden_view_config,
	)

class BaseView(object):
	section = ""
	def __init__(self, request):
		self.request = request
		self.errors = False
		if request.authenticated_userid:
			DBSession.query(User).filter(User.username == request.authenticated_userid).first().lastseen = datetime.utcnow()

class BaseAdminView(BaseView):
	def error_redirect(self, msg, location='admin_home', route=True, **kwargs):
		"""Flash msg and redirect"""
		self.request.session.flash(msg)
		log.error("WHAT HAPPENED? %s" % msg)
		if route:
			raise HTTPFound(location=self.request.route_url(location, **kwargs))
		else:
			raise HTTPFound(location=location)

	def flash(self, msg):
		self.request.session.flash(msg)
		self.errors = True

	# TODO: This currently isn't used at the moment. Turned out it didn't actually do what I wanted it to
	#	I might need to actually commit the session then attempt flush to catch DB consistency errors.
	def doFlush(self, item=None, **kwargs):
		try:
			pass
			DBSession.flush()
		except DBAPIError as e:
			log.error(format_exc())
			DBSession.rollback()
			if item:
				if item.id:
					self.error_redirect("Database error: %s" % e, location="admin_%s_edit" % item.__tablename__, id=item.id, **kwargs)
				else:
					self.error_redirect("Database error: %s" % e, location="admin_%s_list" % item.__tablename__, **kwargs)
			else:
				self.error_redirect("Database error: %s" % e, **kwargs)

	def getItem(self, CLS, _id, errloc='admin_home', route=True, polymorphic=False, **kwargs):
		if _id:
			try: _id = int(_id)
			except ValueError: self.error_redirect("%s (%s) not found." % (CLS.__name__, _id),
				errloc, route, **kwargs)
			if polymorphic:
				return DBSession.query(CLS).with_polymorphic('*').get(_id)
			else:
				return DBSession.query(CLS).get(_id)
		else:
			return None

	# Only really used from getItemOrCreate, and admin_del
	def getItemOrFail(self, CLS, _id, **kwargs):
		item = self.getItem(CLS, _id, **kwargs)
		if not item:
			self.error_redirect("%s (%s) not found." % (CLS.__name__, _id), location="admin_%s_list" % CLS.__tablename__, **kwargs)
		return item

	# Only used from non-associative lists
	def getItemOrCreate(self, CLS, param='id', **kwargs):
		md = self.request.matchdict
		if param in md:
			item = self.getItemOrFail(CLS, md[param], **kwargs)
		else: #new
			item = CLS()
		return item

	def parseInt(self, i):
		if i:
			try: return int(i)
			except ValueError as e:
				self.request.session.flash("Warning: %s is not an integer. Not storing." % i)
		return None

	def parseDate(self, param, format):
		params = self.request.params
		if param in params:
			if params[param]:
				try:
					return datetime.strptime(params[param], format)
				except ValueError as e:
					self.request.session.flash("Warning: %s. Not storing. (%s)" % (str(e), params[param]))
		return None

	def parseStr(self, param, strParserMeth=None):
		s = self.request.params.get(param, None)
		if s is None: return None
		try:
			if strParserMeth:
				return strParserMeth(s.encode("ascii"))
			else:
				return s.encode("ascii")
		except UnicodeEncodeError:
			self.request.session.flash("Warning: (%s) has non ASCII characters. Not stored." % s)
		return None

	def setStrUniValue(self, item, attr, value):
		if value:
			if not item.checkLen(attr, value):
				self.request.session.flash("Warning: (%s) is too long. Truncating." % s)
			setattr(item, attr, value)
		else:
			setattr(item, attr, None)

	def parseEnum(self, param, CLS):
		if param not in self.request.params:
			self.flash("Missing type in %s. Value not stored/changed." % CLS.__name__)
		try: return CLS(self.request.params[param])
		except ValueError:
			self.flash("Incorrect type in %s. Value not stored/changed. (%s)" % (CLS.__name__, self.request.params[param]))

	def getPaginatePage(self, q, items_per_page=10):
		request = self.request
		query_params = request.params.mixed()
		try: page = int(request.params.get("page", 1))
		except ValueError: page = 1
		def url_maker(link_page):
		    query_params['page'] = link_page
		    return request.current_route_url(_query=query_params)
		return SqlalchemyOrmPage(q, page, items_per_page=items_per_page,
		                     url_maker=url_maker)

	def setAttrIfChanged(self, item, param, parserMethod=None, *parserArgs, **parserkwArgs):
		params = self.request.params
		if param in params:
			if parserMethod:
				val = parserMethod(param, *parserArgs, **parserkwArgs)
				if val is None: return
				if val != parserMethod(param+"_orig", *parserArgs, **parserkwArgs):
					setattr(item, param, val)
			else:
				val = params[param]
				if val != params[param+"_orig"]:
					setattr(item, param, val)

	def setAttrIfChangedCheckBox(self, assocs, param, person=False):
		params = self.request.params
		check = params.getall(param)
		print("\nCHECKING %s\n" % param)
		print(params)
		if param+"_orig" not in params: return
		check_orig = params.get(param+"_orig", "")
		if check_orig: check_orig = set(check_orig.split(","))
		else: check_orig = set()
		check_diff = check_orig.symmetric_difference(check)
		for item in assocs:
			spid = str(item.person_id)
			if spid in check_diff:
				print("MODDING: %s" % spid)
				if spid in check:
					if person: setattr(item.person, param, True)
					else: setattr(item, param, True)
				else:
					if person: setattr(item.person, param, False)
					else: setattr(item, param, False)

class LoginOutView(BaseView):
	# http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/tutorials/wiki2/authorization.html
	@view_config(route_name='login', renderer='login.mako')
	@forbidden_view_config(renderer='login.mako')
	def login(self):
		request = self.request
		login_url = request.route_url('login')
		referrer = request.url
		if referrer == login_url:
			referrer = '/' # never use the login form itself as came_from
		came_from = request.params.get('came_from', referrer)
		message = ''
		username = ''
		password = ''
		if 'form.submitted' in request.params:
			username = request.params['username']
			password = request.params['password']
			if password and User.check_user_pass(username, password):
				headers = remember(request, username)
				return HTTPFound(location = came_from,
					headers = headers)
			message = 'Failed login'

		return dict(
			message = message,
			url = request.application_url + '/login',
			came_from = came_from,
			username = username,
			password = password,
			section = "Log in",
		)

	@view_config(route_name='logout')
	def logout(self):
		request = self.request
		headers = forget(request)
		return HTTPFound(location = request.route_url('admin_home'),
			headers = headers)
