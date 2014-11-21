from logging import getLogger
log = getLogger(__name__)

from traceback import format_exc

from pyramid.httpexceptions import (
	HTTPFound,
	HTTPNotFound,
	)

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from confapp.models import (
	DBSession,
	)

from webhelpers.paginate import PageURL_WebOb, Page

class BaseView(object):
	section = ""
	def __init__(self, request):
		self.request = request
		

class BaseAdminView(BaseView):
	def error_redirect(self, msg, location, route=True, **kwargs):
		"""Will abort any DB transaction, and rollback... probably"""
		self.request.session.flash(msg)
		if route:
			raise HTTPFound(location=self.request.route_url(location, **kwargs))
		else:
			raise HTTPFound(location=location)
	
	def doFlush(self, routetype, id=None, **kwargs):
		try:
			DBSession.flush()
		except DBAPIError as e:
			log.error(format_exc())
			#DBSession.rollback()
			self.idErrorRedirect("Database error: %s" % e, routetype, id, **kwargs)
	
	def getItem(self, CLS, _id, errloc='admin_home', route=True, polymorphic=False, **kwargs):
		if _id:
			try: _id = int(_id)
			except ValueError: self.error_redirect("%s (%s) not found." % (CLS.typename, _id), 
				errloc, route, **kwargs)
			if polymorphic:
				return DBSession.query(CLS).with_polymorphic('*').get(_id)
			else:
				return DBSession.query(CLS).get(_id)
		else:
			return None
	
	def getItemOrFail(self, CLS, _id, errloc='admin_home', route=True, **kwargs):
		item = self.getItem(CLS, _id, errloc='admin_home', route=True, **kwargs)
		if not item:
			self.error_redirect("%s (%s) not found." % (CLS.typename, _id), errloc, route, **kwargs)
		return item
	
	def getItemOrCreate(self, CLS, route, param='id', **kwargs):
		md = self.request.matchdict
		if param in md:
			item = self.getItemOrFail(CLS, md[param], route, **kwargs)
		else: #new
			item = CLS()
		return item
		
	def idErrorRedirect(self, msg, routetype, id=None, listing=False, hybrid=False, **kwargs):
		if listing:
			loc = 'admin_%s_list' % routetype
		else:
			if hybrid:
				loc = 'admin_%s_edit' % routetype
			elif id:
				loc = 'admin_%s_edit' % routetype
			else:
				loc = 'admin_%s_new' % routetype
		self.error_redirect(msg, loc, id=id, **kwargs)
	
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
					self.request.session.flash("Warning: %s. Not storing." % str(e))
		return None
		
	def parseStr(self, s):
		if not s: return None
		try: return s.encode("ascii")
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

	def parseEnum(self, param, CLS, routetype, id=None, **kwargs):
		if param not in self.request.params:
			self.idErrorRedirect("Missing type in %s." % CLS.__name__, routetype, id, **kwargs)
		try: return CLS.from_string(self.request.params[param])
		except ValueError: 
			self.idErrorRedirect("Incorrect type in %s." % CLS.__name__, routetype, id, **kwargs)

	def getPaginatePage(self, q, items_per_page=10):
		try: current_page = int(self.request.params["page"])
		except KeyError, ValueError: current_page = 1
		page_url = PageURL_WebOb(self.request)
		return Page(q, page=current_page, items_per_page=items_per_page, url=page_url)
