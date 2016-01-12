from logging import getLogger
log = getLogger(__name__)

from traceback import format_exc

from pyramid.view import (
	view_config,
	forbidden_view_config,
	view_defaults,
	)

from pyramid.httpexceptions import (
	HTTPFound,
	)

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import (
	noload,
	contains_eager,
	joinedload,
	undefer,
)

from sqlalchemy.sql import func

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
	TripLogger,
	Helper,
	FRIENDLYDAYMAP,
	CLASSMAPPER,
	sortstripstring,
	)

from time import time

ORDER_BY_MAP = {
	"" : (Person.lastname, Person.firstname),
	"code" : (Session.code, Association.registered),
}

class DummyPage:
	def __init__(self, items):
		self.items = items
	def pager(self):
		return ""

def sports_helper(item):
	if item.session.building == "1": sport = True
	else: sport = False
	if sport:
		sporttick = u"Y" if item.registered_sport else u"N"
	else:
		sporttick = ""
	return sporttick

class AdminListing(BaseAdminView):
	@view_config(route_name='admin_day_search', renderer='admin_listing.mako', permission='checkin')
	@view_config(route_name='admin_day_search_n', renderer='admin_listing.mako', permission='checkin')
	@view_config(route_name='admin_day_search_c', renderer='admin_listing.mako', permission='checkin')
	def admin_entry_search(self):
		md = self.request.matchdict
		day = md.get("day")
		name = md.get("name")
		code = md.get("code")
		log.debug("\n\n??? %s" % md)
		return self.do_entry_search(day, name, code)	
	
	@view_config(route_name='admin_day_list', renderer='admin_listing.mako', permission='checkin')
	def admin_entry_list(self):
		md = self.request.matchdict
		params = self.request.params
		day = md.get("day")
		name = params.get("search.name")
		code = params.get("search.code")

		return self.do_entry_search(day, name, code)
		
	@view_config(route_name='admin_special_list', renderer='admin_special.mako', permission='checkin')
	def admin_special_list(self):
		request = self.request
		md = request.matchdict
		day = md.get("day")
		if not day:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "admin_home")
		day = FRIENDLYDAYMAP.get(day.lower())
		if not day:
			self.error_redirect("Bad day.", "admin_home")
		
		page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
			options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
			filter(Session.day == day).order_by(Session.code).all())
		return dict(section=day, page=page)

	@view_config(route_name='admin_csv_list', renderer='csv', permission='checkin')
	def admin_csv_list(self):
		request = self.request
		items = DBSession.query(Association).join(Association.session, Association.person).\
			options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
			order_by(Session.code).all()
		header = ["Main", "Sports", "First name", "Last name", "E-mail", "Type", "Code", "Session title", "Evals", "Handouts", "Comment"]
		rows = (
			(
				u"Y" if item.registered else u"N",
				sports_helper(item),
				item.person.firstname,
				item.person.lastname,
				item.person.email.strip().replace("\n", ";") if item.person.email else "",
				str(item.type),
				item.session.code,
				item.session.title,
				str(item.session.evaluations),
				str(item.session.handouts),
				item.session.comments if item.session.comments else "",
			)
			for item in items
		)
		return dict(header=header, rows=rows)
		
	def do_entry_search(self, day, name, code):
		if not day:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "admin_home")
		day = FRIENDLYDAYMAP.get(day.lower())
		if not day:
			self.error_redirect("Bad day.", "admin_home")
		log.debug("\n\nSEARCHING: %s OR %s\n" % (name, code))
		
		order_by = ORDER_BY_MAP.get(self.request.params.get("sort", ""),(Person.lastname, Person.firstname))
		
		if name and code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day, Session.code == code).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname).all())
			if len(page.items) < 1:
				page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
					options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
					filter(Session.day == day, Session.code.like("%s%%" % code)).\
					filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
					order_by(*order_by).all())
		elif name:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(*order_by).all())
		elif code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day, Session.code == code).order_by(*order_by).all())
			if len(page.items) < 1:
				print "NO CODE ITEMS??"
				page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
					options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
					filter(Session.day == day, Session.code.like("%s%%" % code)).order_by(*order_by).all())
		else:
			page = self.getPaginatePage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day).order_by(*order_by), 30)
		
		return dict(section=day, page=page, name=name, code=code, marker=self.request.params.get("marker"), 
			time=time(), logged_in=self.request.authenticated_userid, helpers=self.request.registry.settings["helpers"] == "true")
	

	@view_config(route_name='admin_session_list', renderer='admin_session_list.mako', permission='checkin')
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
		return dict(section="session", page=page, title=title, code=code, logged_in=self.request.authenticated_userid)
			
	@view_config(route_name='admin_person_list', renderer='admin_person_list.mako', permission='checkin')
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
		
		return dict(section="person", page=page, logged_in=self.request.authenticated_userid)
		
	@view_config(route_name='admin_helper_list', renderer='admin_helper_list.mako', permission='checkin')
	def admin_helper_list(self):
		helpers = DBSession.query(Helper).order_by(Helper.away, Helper.dispatched, Helper.firstname).all()
		return dict(section="helper", items=helpers, time=time())

	@view_config(route_name='admin_times', renderer='admin_times.mako', permission='checkin')
	def admin_times(self):
		times = DBSession.query(TripLogger.building, func.avg(TripLogger.time_total).label('time_avg'))\
			.group_by(TripLogger.building).all()
		return dict(section="Trip times", items=times, logged_in=self.request.authenticated_userid)

	@view_config(route_name='admin_helper_update', renderer='admin_helper_update.mako', permission='checkin')
	def admin_helper_update(self):
		return dict(time=time(), logged_in=self.request.authenticated_userid,
			items=DBSession.query(Helper).order_by(Helper.away, Helper.dispatched, Helper.firstname).all())


class AdminEdit(BaseAdminView):
	@view_config(route_name='admin_day_edit_n', renderer='admin_day_edit.mako', permission='checkin')	
	@view_config(route_name='admin_day_edit_c', renderer='admin_day_edit.mako', permission='checkin')	
	@view_config(route_name='admin_day_edit_nc', renderer='admin_day_edit.mako', permission='checkin')	
	@view_config(route_name='admin_day_edit', renderer='admin_day_edit.mako', permission='checkin')	
	def admin_day_edit(self):
		request = self.request
		params = request.params
		
		md = request.matchdict
		name = md.get("name")
		code = md.get("code")
		
		if not name:
			name = params.get("name")
		if not code:
			code = params.get("code")
		
		log.debug("\n\nNAME: %s CODE: %s\n\n" % (name, code))
		
		sid = md.get("session")
		pid = md.get("person")
		oday = md.get("day")
		if not oday:
			#error_redirect(self, msg, location, route=True, **kwargs):
			self.error_redirect("Bad day.", "admin_home")
		day = FRIENDLYDAYMAP.get(oday.lower())
		if not day:
			self.error_redirect("Bad day.", "admin_home")
		
		referer = request.referer
		if (not referer) or (referer == request.current_route_url()):
			referer = request.route_url('admin_day_list', day=oday)
		else:
			if "marker" not in referer:
				m = "%s-%s#%s-%s" % (sid, pid, sid, pid)
				if "?" in referer:
					referer += "&marker=%s" % (m)
				else:
					referer += "?marker=%s" % (m)
		came_from = request.params.get('came_from', referer)
		#.options(joinedload(Association.person), joinedload(Association.session)).order_by(Association.person_id)
		item = DBSession.query(Association).filter(Association.person_id == pid, Association.session_id== sid)\
			.options(joinedload(Association.person), joinedload(Association.session))\
			.options(undefer("session._facilities_req"), undefer("session._facilities_got")).order_by(Association.person_id).first()
		if not item:
			self.error_redirect("Entry (p%s,s%s) not found. This person was perhaps removed from the session." % (pid, sid), location=came_from, route=False)
		
		helpers_show = request.registry.settings["helpers"] == "true"
		person = item.person
		session = item.session
		assocs = session.assoc
		if 'form.submitted' in params or 'form.cancelled' in params:
			if 'form.submitted' in params:
				error = False
				sid = session.id
				pid = person.id
				
				# process register checks
				self.setAttrIfChangedCheckBox(assocs, "registered")
						
				# process sport register checks
				self.setAttrIfChangedCheckBox(assocs, "registered_sport")
							
				self.setAttrIfChanged(session, 'equipment', parserMethod=self.parseStr)
				self.setAttrIfChanged(session, 'equip_returned', parserMethod=self.parseStr)
				
				self.setAttrIfChanged(session, 'handouts', self.parseEnum, HandoutType)
				self.setAttrIfChanged(session, 'evaluations', self.parseEnum, HandoutType)
				
				self.setAttrIfChanged(session, 'other')
				self.setAttrIfChanged(session, 'comments')
				
				if helpers_show:
					helper = params.get("helper")
					if helper:
						try:
							helper = DBSession.query(Helper).filter(Helper.away==False, Helper.session == None, Helper.id == helper).one()
							if not helper:
								error = True
								self.request.session.flash("Error: Cannot assign Helper. Please select another." )
							else:
								helper.session = session
								helper.returned = None
								helper.dispatched = time()
						except (NoResultFound, MultipleResultsFound):
							error = True
							self.request.session.flash("Error: Cannot assign Helper. Please select another." )
				
				# TODO: attempt to do DB.commit/flush to catch any DB backend errors
				self.doFlush(location="admin_day_list", day=oday, session=sid, person=pid)
						
				anchor = "%s-%s" % (sid, pid)
				query = (("marker", anchor),)
				if error:
					if name and code:
						return HTTPFound(location=request.route_url('admin_day_edit_nc', session=sid, person=pid, day=oday, name=name, code=code, _anchor=anchor, _query=query))
					elif name:
						return HTTPFound(location=request.route_url('admin_day_edit_n', session=sid, person=pid, day=oday, name=name, _anchor=anchor, _query=query))
					elif code:
						return HTTPFound(location=request.route_url('admin_day_edit_c', session=sid, person=pid, day=oday, code=code, _anchor=anchor, _query=query))
					else:
						return HTTPFound(location=request.route_url('admin_day_edit_c', session=sid, person=pid, day=oday, code=code, _anchor=anchor, _query=query))
			
			anchor = "%s-%s" % (sid, pid)
			query = (("marker", anchor),)
			print "REDIRECT TO:", name, code
			if name and code:
				return HTTPFound(location=request.route_url('admin_day_search', day=oday, name=name, code=code, _anchor=anchor, _query=query))
			elif name:
				return HTTPFound(location=request.route_url('admin_day_search_n', day=oday, name=name, _anchor=anchor, _query=query))
			elif code:
				return HTTPFound(location=request.route_url('admin_day_search_c', day=oday, code=code, _anchor=anchor, _query=query))
			else:
				return HTTPFound(location=request.route_url('admin_day_list', day=oday, _anchor=anchor, _query=query))
		
		if helpers_show:
			helpers = DBSession.query(Helper).filter(Helper.away==False, Helper.session == None).order_by(Helper.away, Helper.returned, Helper.firstname).all()
		else:
			helpers = None
		return dict(section=oday, item=item, person=person, session=session, assocs=assocs, name=name, code=code, helpers=helpers, 
			logged_in=self.request.authenticated_userid, helpers_show=helpers_show)
		
	@view_config(route_name='admin_session_new', renderer='admin_session_edit.mako', permission='checkin')
	@view_config(route_name='admin_session_edit', renderer='admin_session_edit.mako', permission='checkin')	
	def admin_session_edit(self):
		request = self.request
		params = request.params
		
		item = self.getItemOrCreate(Session)
				
		if 'form.submitted' in params or 'form.remove' in params:
			if item.id is None:
				DBSession.add(item)
			
			self.setAttrIfChanged(item, 'day', self.parseEnum, DayType)
			
			self.setAttrIfChanged(item, 'code')
			self.setAttrIfChanged(item, 'title')
			
			self.setAttrIfChanged(item, 'facilitiesReq')
			self.setAttrIfChanged(item, 'facilitiesGot')
			
			self.setAttrIfChanged(item, 'building', parserMethod=self.parseStr)
			self.setAttrIfChanged(item, 'room', parserMethod=self.parseStr)
			self.setAttrIfChanged(item, 'loctype', parserMethod=self.parseStr)
			
			self.setAttrIfChanged(item, 'other')
			self.setAttrIfChanged(item, 'comments')
			
			self.setAttrIfChanged(item, 'equipment', parserMethod=self.parseStr, strParserMeth=sortstripstring)
			self.setAttrIfChanged(item, 'equip_returned', parserMethod=self.parseStr, strParserMeth=sortstripstring)
			
			self.setAttrIfChanged(item, 'handouts', self.parseEnum, HandoutType)
			self.setAttrIfChanged(item, 'evaluations', self.parseEnum, HandoutType)
			
			if 'form.remove' in params:
				try:
					remthis = [int(sess) for sess in params.getall("removeperson")]
				except ValueError as e:
					self.request.session.flash("Warning: Something bad happened: %s" % e)
					self.doFlush(item=item)
					return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))
				log.debug("\n\nREMOVING: %s\n\n" % remthis)
				
				for id in remthis:
					DBSession.query(Association).filter(Association.session_id == item.id, 
						Association.person_id == id).delete()
				if remthis:
					self.request.session.flash("Removed: %s" % remthis)
					
			self.doFlush(item=item)
			
			return HTTPFound(location=request.route_url('admin_session_edit', id=item.id))
		
		return dict(section="session", item=item, came_from="", logged_in=self.request.authenticated_userid,)		
		
	@view_config(route_name='admin_person_new', renderer='admin_person_edit.mako', permission='checkin')
	@view_config(route_name='admin_person_edit', renderer='admin_person_edit.mako', permission='checkin')	
	def admin_person_edit(self):
		request = self.request
		params = request.params
		
		item = self.getItemOrCreate(Person)
				
		if 'form.submitted' in params or 'form.remove' in params:
			DBSession.add(item)
		
			self.setAttrIfChanged(item, "firstname")
			self.setAttrIfChanged(item, "lastname")
			
			self.setAttrIfChanged(item, 'phone', parserMethod=self.parseStr)
			self.setAttrIfChanged(item, 'email', parserMethod=self.parseStr)
			
			# add to session
			sesscode = self.parseStr("addsession")
			if sesscode:
				print "\nADDING TO: %s" % sesscode
				session = None
				if sesscode: session = DBSession.query(Session).filter(Session.code == sesscode).first()
				print "SEARCH RES: %s" % session
				if not session:
					self.request.session.flash("Warning: Session (%s) not found." % sesscode)
				else:
					DBSession.merge(Association(session_id=session.id, person_id=item.id,
						type=self.parseEnum('type', PersonType)))
			
			if 'form.remove' in params:
				try:
					remthis = [int(sess) for sess in params.getall("removesess")]
				except ValueError as e:
					self.request.session.flash("Warning: Something bad happened: %s" % e)
					self.doFlush(item=item)
					return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))
				log.debug("\n\nREMOVING: %s\n\n" % remthis)
				
				for id in remthis:
					DBSession.query(Association).filter(Association.session_id == id, 
						Association.person_id == item.id).delete()
				if remthis:
					self.request.session.flash("Removed session ID(s): %s" % remthis)
			
			self.doFlush(item=item)
				
			return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))
		
		return dict(section="person", item=item, came_from="", logged_in=self.request.authenticated_userid,)
		
		
	@view_config(route_name='admin_helper_new', renderer='admin_helper_edit.mako', permission='checkin')
	@view_config(route_name='admin_helper_edit', renderer='admin_helper_edit.mako', permission='checkin')	
	def admin_helper_edit(self):
		request = self.request
		params = request.params
		
		item = self.getItemOrCreate(Helper)
		
		referer = request.referer
		if (not referer) or (referer == request.current_route_url()):
			referer = request.route_url('admin_helper_list')
		came_from = request.params.get('came_from', referer)
		
		if 'form.submitted' in params:
			DBSession.add(item)
		
			self.setAttrIfChanged(item, "firstname")
			self.setAttrIfChanged(item, "lastname")
			
			self.setAttrIfChanged(item, 'phone', parserMethod=self.parseStr)
			
			check = params.getall("away")
			check_orig = params.get("away_orig") == "True"
			away = True if "True" in check else False
			if check_orig != away:
				if away and not item.away:
					item.dispatched = time()
				item.away = away
			
			self.setAttrIfChanged(item, "comment")
			
			self.doFlush(item=item)
				
			return HTTPFound(location=came_from)
		
		return dict(section="helper", item=item, came_from=came_from, logged_in=self.request.authenticated_userid,)
		
	@view_config(route_name='admin_helper_returned_list', permission='checkin')
	def admin_helper_returned_list(self):	
		self.admin_helper_returned()
		return HTTPFound(location=request.route_url('admin_helper_list'))

	@view_config(route_name='admin_helper_returned', permission='checkin')
	def admin_helper_returned(self):
		request = self.request
		params = request.params
		
		helperlist = request.route_url('admin_helper_list')
		if request.referer and request.referer == helperlist:
			redirect = helperlist
		else:
			redirect = request.route_url('admin_helper_update')
		
		item = self.getItem(Helper, request.matchdict['id'], errloc=redirect, route=False)
		if item:
			# log trip data
			item.returned = time()
			session = item.session
			t1 = item.dispatched
			t2 = item.returned
			total = t2-t1
			if item.session:
				DBSession.add(TripLogger(helper_id=item.id, session_id=session.id, 
					time_departed=t1, time_returned=t2, code=session.code,
					building=session.building, time_total=total))
			item.session = None
			item.dispatched = None
			self.doFlush(item=item)
					
		return HTTPFound(location=redirect)
			

class AdminDelete(BaseAdminView):
	@view_config(route_name='admin_del', renderer='admin_del.mako', permission='admin')
	def admin_del(self):
		request = self.request
		params = request.params
		md = request.matchdict
		
		type = CLASSMAPPER.get(request.matchdict.get("type"), "")
		if not type:
			self.error_redirect("Type not specified.", "admin_home")
		item = self.getItemOrFail(type, md.get("id"))
		
		if request.referer:
			came_from = request.referer
		else:
			came_from = request.route_url('admin_%s_update' % type.__tablename__, item.id)
		
		return dict(section=type.__tablename__.title(), item=item, came_from=came_from, logged_in=self.request.authenticated_userid,)
		
	@view_config(route_name='admin_del_4real', permission='admin')
	def admin_del_4real(self):
		request = self.request
		params = request.params
		md = request.matchdict
		
		type = CLASSMAPPER.get(request.matchdict.get("type"), "")
		if not type:
			self.error_redirect("Type not specified.", "admin_home")
		item = self.getItemOrFail(type, md.get("id"))
		
		DBSession.delete(item)
		
		self.flash("Deleted %s" % item.label())
		return HTTPFound(location=request.route_url('admin_%s_list' % type.__tablename__,))

class SplashView(BaseAdminView):
	@view_config(route_name='admin_home', renderer='admin_home.mako', permission='splash')
	def home(self):
		return dict(section="home", logged_in=self.request.authenticated_userid,)

	@view_config(route_name='admin_special_home', renderer='admin_special_home.mako', permission='splash')
	def special_home(self):
		return dict(section="home", logged_in=self.request.authenticated_userid,)

