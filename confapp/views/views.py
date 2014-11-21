from logging import getLogger
log = getLogger(__name__)

from traceback import format_exc

from pyramid.view import (
	view_config,
	view_defaults,
	)
from pyramid.httpexceptions import (
	HTTPFound,
	)

from sqlalchemy.exc import DBAPIError

from sqlalchemy.orm import (
	noload,
	contains_eager,
)

from confapp.views import (
	BaseAdminView,
	)
	
from confapp.models import (
	DBSession,
	Person,
	Session,
	Association,
	DayType,
	HandoutType,
	PersonType,
	FRIENDLYDAYMAP,
	)

class DummyPage:
	def __init__(self, items):
		self.items = items
	def pager(self):
		return ""

class AdminListing(BaseAdminView):
	@view_config(route_name='admin_day_search', renderer='admin_listing.mako')
	@view_config(route_name='admin_day_search_n', renderer='admin_listing.mako')
	@view_config(route_name='admin_day_search_c', renderer='admin_listing.mako')
	def admin_entry_search(self):
		md = self.request.matchdict
		params = self.request.params
		day = md.get("day")
		name = md.get("name")
		code = md.get("code")
		log.debug("\n\n??? %s" % md)
		return self.do_entry_search(day, name, code)	
	
	@view_config(route_name='admin_day_list', renderer='admin_listing.mako')
	def admin_entry_list(self):
		md = self.request.matchdict
		params = self.request.params
		day = md.get("day")
		name = params.get("search.name")
		code = params.get("search.code")

		return self.do_entry_search(day, name, code)
		
	@view_config(route_name='admin_special_list', renderer='admin_special.mako')
	def admin_special_list(self):
		md = self.request.matchdict
		params = self.request.params
		day = md.get("day")
		if not day:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "home")
		day = FRIENDLYDAYMAP.get(day.lower())
		if not day:
			self.error_redirect("Bad day.", "home")
		
		page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
			options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
			filter(Session.day == day).order_by(Session.code).all())
		return dict(section=day, page=page)
		
	def do_entry_search(self, day, name, code):
		if not day:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "home")
		day = FRIENDLYDAYMAP.get(day.lower())
		if not day:
			self.error_redirect("Bad day.", "home")
		log.debug("\n\nSEARCHING: %s OR %s\n" % (name, code))
		
		if name and code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day, Session.code == code).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname).all())
		elif name:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname).all())
		elif code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day, Session.code == code).order_by(Person.lastname, Person.firstname).all())
		else:
			page = self.getPaginatePage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day).order_by(Person.lastname, Person.firstname), 30)
		return dict(section=day, page=page, name=name, code=code, marker=self.request.params.get("marker"))
	

	@view_config(route_name='admin_session_list', renderer='admin_session_list.mako')
	def admin_session_list(self):
		params = self.request.params
		title = params.get("search.title")
		code = params.get("search.code")
		if title and code:
			page = self.getPaginatePage(DBSession.query(Session).\
				filter(Session.code == code, Session.title.like("%s%%" % title).order_by(Session.code)), 30)
		elif title:
			page = self.getPaginatePage(DBSession.query(Session).filter(Session.title.like("%%%s%%" % title)).order_by(Session.code), 30)
		elif code:
			page = DummyPage(DBSession.query(Session).filter(Session.code == code).order_by(Session.code))
		else:
			page = self.getPaginatePage(DBSession.query(Session).order_by(Session.code), 30)
		return dict(section="session", page=page, title=title, code=code)
			
	@view_config(route_name='admin_person_list', renderer='admin_person_list.mako')
	def admin_person_list(self):
		params = self.request.params
		name = params.get("search.name")
		code = params.get("search.code")
		if name and code:
			page = self.getPaginatePage(DBSession.query(Person).\
				join(Person.assoc).join(Session.assoc).filter(Session.code == code).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname), 30)
		elif name:
			page = self.getPaginatePage(DBSession.query(Person).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname), 30)
		elif code:
			page = self.getPaginatePage(DBSession.query(Person).\
				join('person.assoc').join('association.session_id').filter(Session.code == code).\
				order_by(Person.lastname, Person.firstname), 30)
		else:
			page = self.getPaginatePage(DBSession.query(Person).order_by(Person.lastname, Person.firstname), 30)
		return dict(section="person", page=page)


class AdminEdit(BaseAdminView):
	@view_config(route_name='admin_day_edit_n', renderer='admin_day_edit.mako')	
	@view_config(route_name='admin_day_edit_c', renderer='admin_day_edit.mako')	
	@view_config(route_name='admin_day_edit_nc', renderer='admin_day_edit.mako')	
	@view_config(route_name='admin_day_edit', renderer='admin_day_edit.mako')	
	def admin_day_edit(self):
		request = self.request
		params = request.params
		
		md = request.matchdict
		name = md.get("name")
		code = md.get("code")
		
		log.debug("\n\nNAME: %s CODE: %s\n\n" % (name, code))
		
		sid = md.get("session")
		pid = md.get("person")
		day = md.get("day")
		if not day:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "home")
		day = FRIENDLYDAYMAP.get(day.lower())
		if not day:
			self.error_redirect("Bad day.", "home")
		
		current_url = request.current_route_url()
		referer = request.referer
		if (not referer) or (referer == current_url):
			referer = request.route_url('admin_day_list', day=day.description)
		else:
			if "marker" not in referer:
				m = "%s-%s#%s-%s" % (sid, pid, sid, pid)
				if "?" in referer:
					referer += "&marker=%s" % (m)
				else:
					referer += "?marker=%s" % (m)
		came_from = request.params.get('came_from', referer)
		
		item = DBSession.query(Association).filter(Association.person_id == pid, Association.session_id== sid).first()
		if not item:
			self.error_redirect("Entry (p%s,s%s) not found." % (pid, sid), "admin_day_list")
		
		person = item.person
		session = item.session
		if 'form.submitted' in params:
			check = params.getall("special")
			special = True if "True" in check else False

			person.firstname = params.get('firstname', u"")
			person.lastname = params.get('lastname', u"")
			
			person.phone = self.parseStr(params.get('phone'))
			person.email = self.parseStr(params.get('email'))
			
			#item.type = self.parseEnum('type', PersonType, "day_person", day=day.description, id=item.id)
			
			check = params.getall("registered")
			item.registered = True if "True" in check else False
			item.type = self.parseEnum('type', PersonType, "day", day=day.description, 
				session=session.id, person=person.id, hybrid=True)
			
			session.title = params.get('sesstitle', u"")
			
			tequip = self.parseStr(params.get('equipment'))
			tequip_ret = self.parseStr(params.get('equip_returned'))
			log.debug("\n\nSPECIAL? %s tequip: %s\n\n" % (special, tequip))
			if special:
				session.equipment = tequip
				session.equip_returned = tequip_ret
			else:
				if not session.equipment:
					session.equipment = tequip
				else:
					if tequip:
						session.equipment = tequip
				if not session.equip_returned:
					session.equip_returned = tequip_ret
				else:
					if tequip_ret:
						session.equip_returned = tequip_ret
			
			thandout = self.parseEnum('handouts', HandoutType, "day", 
				day=day.description, session=session.id, person=person.id)
			if special:
				session.handouts = thandout
			else:
				if session.handouts == HandoutType.pending:
					session.handouts = thandout
				else:
					if thandout != HandoutType.pending:
						session.handouts = thandout
			
			teval = self.parseEnum('evaluations', HandoutType, "day", 
				day=day.description, session=session.id, person=person.id)
			if special:
				session.evaluations = teval
			else:
				if session.evaluations == HandoutType.pending:
					session.evaluations = teval
				else:
					if teval != HandoutType.pending:
						session.evaluations = teval
			
			session.other = params.get('other')
			session.comments = params.get('comments')
			
			anchor = "%s-%s" % (session.id, person.id)
			query = (("marker", anchor),)
			
			try:
				DBSession.flush()
			except DBAPIError as e:
				log.error(format_exc())
				self.idErrorRedirect("Database error: %s" % e, "day",
					session=session.id, person=person.id)
			
			name = params.get("name")
			code = params.get("code")
			
			if name and code:
				return HTTPFound(location=request.route_url('admin_day_search', day=day, name=name, code=code, _anchor=anchor, _query=query))
			elif name:
				return HTTPFound(location=request.route_url('admin_day_search_n', day=day, name=name, _anchor=anchor, _query=query))
			elif code:
				return HTTPFound(location=request.route_url('admin_day_search_c', day=day, code=code, _anchor=anchor, _query=query))
			else:
				return HTTPFound(location=request.route_url('admin_day_list', day=day, _anchor=anchor, _query=query))
		
		return dict(section=session.day, item=item, name=name, code=code)
		
	@view_config(route_name='admin_session_new', renderer='admin_session_edit.mako')
	@view_config(route_name='admin_session_edit', renderer='admin_session_edit.mako')	
	def admin_session_edit(self):
		request = self.request
		params = request.params
		
		#item = self.getItemOrFail(CLS, md[param], route, **kwargs)
		#item = self.getItemOrCreate(Person, 'admin_person_list')
		item = self.getItemOrCreate(Session, 'admin_session_list')
				
		if 'form.submitted' in params:
			if item.id is None:
				DBSession.add(item)
		
			item.firstname = params.get('firstname', u"")
			item.lastname = params.get('lastname', u"")
			
			item.day = self.parseEnum('day', DayType, "day", id=item.id)
			
			item.code = params.get('code', u"")
			item.title = params.get('sesstitle', u"")
			
			item.facilities = params.get('facilities')
			
			item.location = self.parseStr(params.get('location'))
			item.loctype = self.parseStr(params.get('loctype'))
			
			item.other = params.get('other')
			item.comments = params.get('comments')
			
			item.equipment = self.parseStr(params.get('equipment'))
			item.equip_returned = self.parseStr(params.get('equip_returned'))
			
			item.handouts = self.parseEnum('handouts', HandoutType, "day", id=item.id)
			item.evaluations = self.parseEnum('evaluations', HandoutType, "day", id=item.id)
			
			try:
				DBSession.flush()
			except DBAPIError as e:
				log.error(format_exc())
				self.idErrorRedirect("Database error: %s" % e, item.id)
			
			return HTTPFound(location=request.route_url('admin_session_edit', id=item.id))
		
		return dict(section="session", item=item, came_from="")		
		
	@view_config(route_name='admin_person_new', renderer='admin_person_edit.mako')
	@view_config(route_name='admin_person_edit', renderer='admin_person_edit.mako')	
	def admin_person_edit(self):
		request = self.request
		params = request.params
		
		#item = self.getItemOrFail(CLS, md[param], route, **kwargs)
		#item = self.getItemOrCreate(Project, 'admin_project_list')
		item = self.getItemOrCreate(Person, 'admin_person_list')
				
		if 'form.submitted' in params or 'form.remove' in params:
			DBSession.add(item)
		
			item.firstname = params.get('firstname', u"")
			item.lastname = params.get('lastname', u"")
			
			item.phone = self.parseStr(params.get('phone'))
			item.email = self.parseStr(params.get('email'))
			
			# try to attach to session:
			#def getItem(self, CLS, _id, errloc='admin_home', route=True, polymorphic=False, **kwargs):
			
			sesscode = params.get("addsession")
			if sesscode:
				sesscode = self.parseStr(sesscode)
				session = None
				if sesscode: session = DBSession.query(Session).filter(Session.code == sesscode).first()
				if not session:
					self.request.session.flash("Warning: Session (%s) not found." % sesscode)
				else:
					DBSession.merge(Association(session_id=session.id, person_id=item.id,
						type=self.parseEnum('type', PersonType, "person", id=item.id)))
			
			if 'form.remove' in params:
				try:
					remthis = [int(sess) for sess in params.getall("removesess")]
				except ValueError as e:
					self.request.session.flash("Warning: Something bad happened: %s" % e)
					self.doFlush("person", id=item.id)
					return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))
				log.debug("\n\nREMOVING: %s\n\n" % remthis)
				
				for id in remthis:
					DBSession.query(Association).filter(Association.session_id == id, 
						Association.person_id == item.id).delete()
				if remthis:
					self.request.session.flash("Removed: %s" % remthis)
			
			self.doFlush("person", id=item.id)
				
			return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))
		
		return dict(section="person", item=item, came_from="")
	
@view_config(route_name='home', renderer='admin_home.mako')
def home(request):
	return dict(section="home")


@view_config(route_name='admin_special_home', renderer='admin_special_home.mako')
def special_home(request):
	return dict(section="home")
