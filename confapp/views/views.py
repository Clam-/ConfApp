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
	SessionType,
	Association,
	DayType,
	HandoutType,
	PersonType,
	TripLogger,
	Helper,
	FRIENDLYDAYMAP,
	CLASSMAPPER,
	sortstripstring,
	User,
	UserRole,
	Room,
	Building,
	Base,
	)

from ..libs.helpers import read_csv, convertfile, CODE, CODE2

from time import time
from os import unlink

ORDER_BY_MAP = {
	"" : (Person.lastname, Person.firstname),
	"code" : (Session.code, Association.registered),
}

HITS = 60
class DummyObject(object):
    pass

class DummyPage:
	def __init__(self, items):
		self.items = items
	def pager(self):
		return ""

def sports_helper(item):
	session = item.session
	if session.room and (session.room.building.number == "1"): sport = True #or session.room.building.number == "60"
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
		#log.debug("\n\n??? %s" % md)
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
			filter(Session.day == day).filter(Association.registered == True | Association.registered_sport == True).order_by(Session.code).all())
		return dict(section=day, page=page)
		
	@view_config(route_name='admin_special_home', renderer='admin_special.mako', permission='checkin')
	def admin_special_list(self):
		request = self.request
		page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
			options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
			order_by(Session.code).all())
		return dict(section="special", page=page)

	@view_config(route_name='admin_csv_list', renderer='csv', permission='checkin')
	def admin_csv_list(self):
		request = self.request
		items = DBSession.query(Association).join(Association.session, Association.person).\
			options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
			filter(Session.cancelled == False).\
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
		#log.debug("\n\nSEARCHING: %s OR %s\n" % (name, code))
		
		order_by = ORDER_BY_MAP.get(self.request.params.get("sort", ""),(Person.lastname, Person.firstname))
		
		if name and code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day, Session.code == code).\
				filter(Session.cancelled == False).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname).all())
			if len(page.items) < 1:
				page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
					options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
					filter(Session.day == day, Session.code.like("%s%%" % code)).\
					filter(Session.cancelled == False).\
					filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
					order_by(*order_by).all())
		elif name:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.day == day).\
				filter(Session.cancelled == False).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(*order_by).all())
		elif code:
			page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.cancelled == False).\
				filter(Session.day == day, Session.code == code).order_by(*order_by).all())
			if len(page.items) < 1:
				print "NO CODE ITEMS??"
				page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
					options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
					filter(Session.cancelled == False).\
					filter(Session.day == day, Session.code.like("%s%%" % code)).order_by(*order_by).all())
		else:
			page = self.getPaginatePage(DBSession.query(Association).join(Association.session, Association.person).\
				options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
				filter(Session.cancelled == False).\
				filter(Session.day == day).order_by(*order_by), HITS)
		
		return dict(section=day, page=page, name=name, code=code, marker=self.request.params.get("marker"), 
			time=time(), helpers=self.request.registry.settings["helpers"] == "true")
	

	@view_config(route_name='admin_session_list', renderer='admin_session_list.mako', permission='checkin')
	def admin_session_list(self):
		params = self.request.params
		title = params.get("search.title")
		code = params.get("search.code")
		if title and code:
			page = self.getPaginatePage(DBSession.query(Session).\
				filter(Session.code == code, Session.title.contains("%s" % title)).order_by(Session.code), HITS)
		elif title:
			page = self.getPaginatePage(DBSession.query(Session).filter(Session.title.contains("%s" % title)).order_by(Session.code), HITS)
		elif code:
			page = DummyPage(DBSession.query(Session).filter(Session.code == code).order_by(Session.code))
		else:
			page = self.getPaginatePage(DBSession.query(Session).order_by(Session.code), 100)
		return dict(section="session", page=page, title=title, code=code, )
			
	@view_config(route_name='admin_person_list', renderer='admin_person_list.mako', permission='checkin')
	def admin_person_list(self):
		params = self.request.params
		name = params.get("search.name")
		code = params.get("search.code")
		if name and code:
			page = self.getPaginatePage(DBSession.query(Person).\
				join(Person.assoc).join(Association.session).filter(Session.code.like("%s%%" % code)).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname), HITS)
		elif name:
			page = self.getPaginatePage(DBSession.query(Person).\
				filter(Person.lastname.like("%s%%" % name) | Person.firstname.like("%s%%" % name)).\
				order_by(Person.lastname, Person.firstname), HITS)
		elif code:
			page = self.getPaginatePage(DBSession.query(Person).\
				join(Person.assoc).join(Association.session).filter(Session.code.like("%s%%" % code)).\
				order_by(Person.lastname, Person.firstname), HITS)
		else:
			page = self.getPaginatePage(DBSession.query(Person).order_by(Person.lastname, Person.firstname), 150)
		
		return dict(section="person", page=page, )
		
	@view_config(route_name='admin_user_list', renderer='admin_user_list.mako', permission='superadmin')
	def admin_user_list(self):
		page = self.getPaginatePage(DBSession.query(User).order_by(User.username), HITS)
		return dict(section="user", page=page)

	@view_config(route_name='admin_room_list', renderer='admin_location_list.mako', permission='checkin')
	def admin_location_list(self):
		page = self.getPaginatePage(DBSession.query(Room).order_by(Room.building_id, Room.name), 100)
		return dict(section="location", page=page)
		
	@view_config(route_name='admin_helper_list', renderer='admin_helper_list.mako', permission='checkin')
	def admin_helper_list(self):
		helpers = DBSession.query(Helper).order_by(Helper.away, Helper.dispatched, Helper.firstname).all()
		return dict(section="helper", items=helpers, time=time())

	@view_config(route_name='admin_times', renderer='admin_times.mako', permission='checkin')
	def admin_times(self):
		times = DBSession.query(TripLogger.building, func.avg(TripLogger.time_total).label('time_avg'))\
			.group_by(TripLogger.building).all()
		return dict(section="Trip times", items=times, )

	@view_config(route_name='admin_helper_update', renderer='admin_helper_update.mako', permission='checkin')
	def admin_helper_update(self):
		return dict(time=time(), items=DBSession.query(Helper).order_by(Helper.away, Helper.dispatched, Helper.firstname).all())


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
		
		#log.debug("\n\nNAME: %s CODE: %s\n\n" % (name, code))
		
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
				self.setAttrIfChangedCheckBox(assocs, "shirtcollect", person=True)
							
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
				
				# TODO: attempt to do commit/flush to catch any DB backend errors
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
			helpers_show=helpers_show)
		
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
		
		return dict(section="session", item=item, came_from="",)		
		
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
			
			item.person_id = item.id
			self.setAttrIfChangedCheckBox([item], "shirtcollect")
			
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
		
		return dict(section="person", item=item, came_from="",)
		
	@view_config(route_name='admin_room_new', renderer='admin_location_edit.mako', permission='checkin')
	@view_config(route_name='admin_room_edit', renderer='admin_location_edit.mako', permission='checkin')	
	def admin_location_edit(self):
		request = self.request
		params = request.params
		
		item = self.getItemOrFail(Room, request.matchdict["id"])
				
		if 'form.submitted' in params or 'form.remove' in params:
			DBSession.add(item)
		
			self.setAttrIfChanged(item, "name")
			self.setAttrIfChanged(item, "buildingName")
			self.setAttrIfChanged(item, "buildingAddr")
			
			self.doFlush(item=item)
				
			return HTTPFound(location=request.route_url('admin_room_edit', id=item.id))
		
		return dict(section="location", item=item, came_from="",)
		
		
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
		
		return dict(section="helper", item=item, came_from=came_from,)
		
	@view_config(route_name='admin_user_new', renderer='admin_user_edit.mako', permission='superadmin')
	@view_config(route_name='admin_user_edit', renderer='admin_user_edit.mako', permission='superadmin')	
	def admin_user_edit(self):
		request = self.request
		params = request.params
		
		item = self.getItemOrCreate(User)
		
		referer = request.referer
		if (not referer) or (referer == request.current_route_url()):
			referer = request.route_url('admin_user_list')
		came_from = request.params.get('came_from', referer)
		
		if 'form.submitted' in params:
			DBSession.add(item)
		
			self.setAttrIfChanged(item, "username")
			self.setAttrIfChanged(item, "name")
			
			self.setAttrIfChanged(item, 'role', self.parseEnum, UserRole)
			
			if "password" in params and params["password"]:
				item.password = params["password"]
			
			self.doFlush(item=item)
				
			return HTTPFound(location=came_from)
		
		return dict(section="user", item=item, came_from=came_from,)
		
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
			came_from = request.route_url('admin_%s_edit' % type.__tablename__, id=item.id)
		
		return dict(section=type.__tablename__.title(), item=item, came_from=came_from,)
		
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
		
class AdminAdmin(BaseAdminView):
	@view_config(route_name='admin_admin', renderer='admin_admin.mako', permission='admin')
	def admin_view(self): return dict(section="admin")

	@view_config(route_name='nuke', renderer='nuke.mako', permission='admin')
	def nuke_view(self): return dict(section="admin")

	@view_config(route_name='nuke_go', permission='admin')
	def nuke_go_view(self):
		from transaction import commit
		meta = Base.metadata
		for table in reversed(meta.sorted_tables):
			if table.name == "user": continue
			print 'Clear table %s' % table
			DBSession.execute(table.delete())
		commit()
		self.request.session.flash('Deleted all entries.')
		return HTTPFound(location = self.request.route_url('admin_admin'))
		
	@view_config(route_name='upload', permission='admin')
	def upload_view(self):
		from transaction import commit, abort
		
		request = self.request
		f = request.params['csvfile']
		t = request.params['uploadtype']
		if f == u"":
			request.session.flash('No file selected.')
			return HTTPFound(location = request.route_url('admin_admin'))
		if t == u"":
			request.session.flash('No upload type selected.')
			return HTTPFound(location = request.route_url('admin_admin'))
		filename = f.filename
		# convert input file to realfile
		input_file = convertfile(f.file)
		
		if not filename.endswith(".csv"):
			request.session.flash("(%s) is not a .csv file." % filename)
			return HTTPFound(location = request.route_url('admin_admin'))
		self.sessions = {}
		self.people = {} # [firstname, lastname, email] : Person
		self.rooms = {} # roomname : Room
		self.buildings = {} # number : Building
		try:
			firstrow = True
			for row in read_csv(input_file):
				if firstrow:
					firstrow = False
					continue
				# GO
				if t == u"sessions":
					if not self.processSession(row):
						abort()
						request.session.flash("Failure from processSession")
						return HTTPFound(location = request.route_url('admin_admin')) 
				elif t == "people":
					if not self.processPerson(row):
						abort()
						request.session.flash("Failure from processPerson")
						return HTTPFound(location = request.route_url('admin_admin')) 

				elif t == "shirts":
					if not self.processShirt(row):
						abort()
						request.session.flash("Failure from processShirt")
						return HTTPFound(location = request.route_url('admin_admin'))
				elif t == "hosts":
					if not self.processHost(row):
						abort()
						request.session.flash("Failure from processHost")
						return HTTPFound(location = request.route_url('admin_admin')) 
				elif t == "peopleex":
					if not self.processPersonEx(row):
						abort()
						request.session.flash("Failure from processPersonEx")
						return HTTPFound(location = request.route_url('admin_admin'))
				elif t == "handouts":
					if not self.processHandouts(row):
						abort()
						request.session.flash("Failure from processHanouts")
						return HTTPFound(location = request.route_url('admin_admin')) 
						
				elif t == u"sessionsupdate":
					if not self.processSessionUpdate(row):
						abort()
						request.session.flash("Failure from processSessionUpdate")
						return HTTPFound(location = request.route_url('admin_admin'))
										
			request.session.flash('Upload of (%s) complete.' % filename)
		except UnicodeDecodeError:
			request.session.flash("Could not read (%s) correctly. Please upload as 'CSV UTF-8 (Comma Delimited) .csv'" % filename)
			abort()
		unlink(input_file)
		commit()
		return HTTPFound(location = request.route_url('admin_admin'))
	
	def processShirt(self, row):
		firstname = row[4]
		lastname = row[5]
		if firstname and lastname:
			try: 
				p = DBSession.query(Person).filter(Person.firstname == firstname, Person.lastname == lastname).one()
				p.shirt = True
			except NoResultFound:
				pass
		return True
		
		
	def processSession(self, row):
		cancelled = False
		if row[3].startswith("UNAVAILABLE "):
			row[3] = row[3][12:]
			cancelled = True
		c = row[3][0:3]
		if not CODE.match(c): 
			c = row[3][0:4]
			if not CODE2.match(c): c = None
			
		if c and c not in self.sessions:
			if c == "B10":
				print "\n\nDOING B10"
			if not cancelled: room = self.processLocation(row)
			else: room = None
			# Create session
			if cancelled: title = "CANCELLED "+row[3][4:]
			else: title = row[3][4:]
			day = "T" if c[0] in ("A", "B", "C") else "F"
			booked = int(row[5])
			max = int(row[6])
			s = Session(code=c, title=title, sessiontype=SessionType.na, 
				day=DayType.from_string(day), evaluations=HandoutType.pending,
				booked=booked, max=max, room=room, cancelled=cancelled)
			DBSession.add(s)
		return True
		
	def processSessionUpdate(self, row):
		cancelled = False
		if row[3].startswith("UNAVAILABLE "):
			row[3] = row[3][12:]
			cancelled = True
		c = row[3][0:3]
		if not CODE.match(c): 
			c = row[3][0:4]
			if not CODE2.match(c): c = None
			
		if c and c not in self.sessions:
			if c == "B10":
				print "\n\nDOING B10"
			if not cancelled: room = self.processLocationUpdate(row)
			else: room = None
			# Create session
			if cancelled: title = "CANCELLED "+row[3][4:]
			else: title = row[3][4:]
			day = "T" if c[0] in ("A", "B", "C") else "F"
			booked = int(row[5])
			max = int(row[6])
			s = DBSession.query(Session).filter(Session.code == c).one()
			s.max = max
			s.booked = booked
			s.cancelled = cancelled
			s.room = room
		return True
	
	def processLocation(self, row):
		# Create room
		location = [x.strip() for x in row[4].split(",", 2)]
		ex = ""
		# Building
		address = None
		if location[0].startswith("Monash Sport"):
			building = 1
			address = "Scenic Boulevard"
		else:
			#Building 20, Chancellors Walk, S106 Tute Room
			#Basketball Court Near Building 23, College Walk, Exam Halls
			if "Near" in location[0]:
				building = location[0][-2:]
				ex = location[0].split("Building")[0].strip()
			building = int(location[0][-2:])
		# Address
		if not address:
			address = location[1]
		# Room
		if building == 1:
			room = location[1]
		else:
			room = location[2]
		if room in self.rooms:
			return self.rooms[room]
		if building in self.buildings:
			b = self.buildings[building]
		else:
			b = Building(number=building, address=address)
			DBSession.add(b)
			self.buildings[building] = b
		r = Room(name=room)
		r.building = b
		DBSession.add(r)
		self.rooms[room] = r
		return r
		
	def processLocationUpdate(self, row):
		# Create room
		location = [x.strip() for x in row[4].split(",", 2)]
		ex = ""
		# Building
		address = None
		if location[0].startswith("Monash Sport"):
			building = 1
			address = "Scenic Boulevard"
		else:
			#Building 20, Chancellors Walk, S106 Tute Room
			#Basketball Court Near Building 23, College Walk, Exam Halls
			if "Near" in location[0]:
				building = location[0][-2:]
				ex = location[0].split("Building")[0].strip()
			building = int(location[0][-2:])
		# Address
		if not address:
			address = location[1]
		# Room
		if building == 1:
			room = location[1]
		else:
			room = location[2]
		r = DBSession.query(Room).filter(Room.name == room).first()
		if r:
			return r
		b = DBSession.query(Building).filter(Building.number == building).first()
		if not b:
			b = Building(number=building, address=address)
			DBSession.add(b)
		r = Room(name=room)
		r.building = b
		DBSession.add(r)
		return r
		
	def processPerson(self, row):
		# CHECK IF PERSON PRESENTING
		found = False
		for x in row[32:36]:
			if x.strip(): found = True
		if not found: return True
		
		# Create or get Person
		firstname = row[8].strip()
		lastname = row[9].strip()
		email = row[10].strip()
		p = None
		if (firstname, lastname, email) in self.people:
			p = self.people[(firstname, lastname, email)]
		else:
			phone = ("%s\n" % row[11].strip() if row[11].strip() else "") +\
				("%s\n" % row[12].strip() if row[12].strip() else "") +\
				("%s\n" % row[37].strip() if row[37].strip() else "")
			org = row[13].strip()
			if org == "Other":
				org = row[14].strip()
			p = Person(firstname=firstname, lastname=lastname, email=email,
				phone=phone, organisation=org)
			self.people[(firstname, lastname, email)] = p
			DBSession.add(p)
			DBSession.flush()
		
		# Process their session
		#row[32] I am presenting in session/s
		#row[33] Please indicate which elective you are presenting in.	
		#row[34] Please indicate which elective you are presenting in.	
		#row[35] Please indicate which elective you are presenting in.
		for x in row[32:36]:
			# check for multiple sessions in a cell
			x = x.strip()
			if x and CODE.match(x[0:3]):
				self.addPersonToSession(p, x[0:3])
				i = x.find(",")
				while i != -1:
					if CODE.match(x[i+2:i+5]):
						self.addPersonToSession(p, x[i+2:i+5])
					i = x.find(",", i+1)
		return True
		
	def processPersonEx(self, row):
		# Create or get Person
		firstname = row[1].strip()
		lastname = row[2].strip()
		if not firstname or not lastname: return True
		
		p = DBSession.query(Person).filter(Person.firstname == firstname, Person.lastname == lastname).first()
		if not p:
			phone = row[4].strip()
			org = row[3].strip()
			p = Person(firstname=firstname, lastname=lastname, phone=phone, organisation=org)
			DBSession.add(p)
			DBSession.flush()
		# Process their session
		self.addPersonToSession(p, row[0].strip())
		return True
		
	def processHost(self, row):
		# Create or get Person
		firstname = row[0].strip()
		lastname = row[1].strip()
		if not firstname or not lastname: return True
		
		email = row[3].strip()
		p = DBSession.query(Person).filter(Person.firstname == firstname, Person.lastname == lastname).first()
		if not p:
			phone = row[4].strip()
			p = Person(firstname=firstname, lastname=lastname, phone=phone, email=email)
			DBSession.add(p)
			DBSession.flush()
		# Process their session
		for x in row[5:8]:
			print x
			if CODE.match(x[0:3]):
				self.addPersonToSession(p, x[0:3], PersonType.host)
			else:
				print "BAD CODE FOR (%s, %s)" % (firstname, lastname)
				self.request.session.flash("B")
		return True
		
	def processHandouts(self, row):
		# Skip non handout
		if not row[3].strip(): return True
		
		# Process the session
		session = row[0].strip()
		c = session[0:3]
		if not CODE.match(c): 
			c = session[0:4]
			if not CODE2.match(c): c = None
		if c:
			DBSession.query(Session).filter(Session.code == c).one().handouts = HandoutType.pending
		return True
	
	def addPersonToSession(self, p, code, t=PersonType.presenter):
		try: 
			s = DBSession.query(Session).filter(Session.code == code).one()
			if not DBSession.query(Association).filter(Association.person_id == p.id, Association.session_id == s.id).first():
				DBSession.add(Association(person_id=p.id, session_id=s.id, type=t))
			else:
				#self.request.session.flash("Skipping duplicate session (%s) for (%s, %s)" % (code, p.firstname, p.lastname))
				self.request.session.flash("s")
				print "Skipping duplicate session (%s) for (%s, %s)" % (code, p.firstname, p.lastname)
		except NoResultFound:
			self.request.session.flash("x")
			print "Could not find Session: (%s)" % code
		

class SplashView(BaseAdminView):
	@view_config(route_name='admin_home', renderer='admin_home.mako', permission='splash')
	def home(self):
		return dict(section="home",)


