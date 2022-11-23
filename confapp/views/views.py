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
    HandoutSaidType,
    PersonType,
    TripLogger,
    Helper,
    DayType,
    CLASSMAPPER,
    sortstripstring,
    User,
    UserRole,
    Room,
    Building,
    Base,
    Settings,
    TimeCode
    )

from ..libs.helpers import read_csv, convertfile, returnTime, CODE, CODE_PREFIX

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
    if session.sport:
        sporttick = "Y" if item.registered_sport else "N"
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
        day = DayType[day]
        if not day:
            self.error_redirect("Bad day.", "admin_home")

        page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
            options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
            filter(Session.day == day).filter(Association.registered == True | Association.registered_sport == True).order_by(Session.code).all())
        return dict(section=day.name, page=page)

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
                "Y" if item.registered else "N",
                sports_helper(item),
                item.person.firstname,
                item.person.lastname,
                item.person.email.strip().replace("\n", ";") if item.person.email else "",
                item.type.name,
                item.session.code,
                item.session.title,
                item.session.evaluations.name,
                item.session.handouts.name,
                item.session.comments if item.session.comments else "",
            )
            for item in items
        )
        return dict(header=header, rows=rows)

    def do_entry_search(self, day, name, code):
        if not day:
            self.error_redirect("Bad day.", "admin_home")
        day = DayType[day]
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
                print("NO CODE ITEMS??")
                page = DummyPage(DBSession.query(Association).join(Association.session, Association.person).\
                    options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
                    filter(Session.cancelled == False).\
                    filter(Session.day == day, Session.code.like("%s%%" % code)).order_by(*order_by).all())
        else:
            page = self.getPaginatePage(DBSession.query(Association).join(Association.session, Association.person).\
                options(contains_eager(Association.session)).options(contains_eager(Association.person)).\
                filter(Session.cancelled == False).\
                filter(Session.day == day).order_by(*order_by), HITS)

        return dict(section=day.name, page=page, name=name, code=code, marker=self.request.params.get("marker"),
            time=time(), settings=self.settings)


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
        return dict(section="session", page=page, title=title, code=code, settings=self.settings)

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

    @view_config(route_name='unregistered', renderer='admin_listing.mako', permission='checkin')
    def unregistered(self):
        md = self.request.matchdict
        day = md.get("day")
        if not day:
            self.error_redirect("Bad day.", "admin_home")
        day = DayType[day]
        #log.debug("\n\nSEARCHING: %s OR %s\n" % (name, code))
        items = []
        for x in DBSession.query(Session).filter(Session.cancelled == False).\
            filter(Session.day == day).order_by(Session.code):
            registered = False
            for y in x.assoc:
                if y.type == PersonType.Presenter and (y.registered or y.registered_sport):
                    registered = True
            if not registered:
                for y in x.assoc:
                    if y.type == PersonType.Presenter: items.append(y)
        page = DummyPage(items)
        return dict(section=day.name, page=page, name="", code="", marker=self.request.params.get("marker"),
            time=time(), settings = self.settings, unregistered=True)

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
        day = DayType[oday]

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

        helpers_show = self.settings.helpers
        person = item.person
        session = item.session
        assocs = session.assoc
        if 'form.submitted' in params or 'form.cancelled' in params or 'form.add' in params:
            # build edit page redirect URL
            anchor = "%s-%s" % (sid, pid)
            query = (("marker", anchor),)
            if name and code:
                eurl = request.route_url('admin_day_edit_nc', session=sid, person=pid, day=oday, name=name, code=code, _anchor=anchor, _query=query)
            elif name:
                eurl = request.route_url('admin_day_edit_n', session=sid, person=pid, day=oday, name=name, _anchor=anchor, _query=query)
            elif code:
                eurl = request.route_url('admin_day_edit_c', session=sid, person=pid, day=oday, code=code, _anchor=anchor, _query=query)
            else:
                eurl = request.route_url('admin_day_edit', session=sid, person=pid, day=oday, _anchor=anchor, _query=query)
            if 'form.submitted' in params or 'form.add' in params:
                helpererror = False
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
                                helpererror = True
                                self.request.session.flash("Error: Cannot assign Helper. Please select another." )
                            else:
                                helper.session = session
                                helper.returned = None
                                helper.dispatched = time()
                        except (NoResultFound, MultipleResultsFound):
                            helpererror = True
                            self.request.session.flash("Error: Cannot assign Helper. Please select another." )

                # TODO: attempt to do commit/flush to catch any DB backend errors
                self.doFlush(location="admin_day_list", day=oday, session=sid, person=pid)

                if helpererror:
                    if name and code:
                        return HTTPFound(location=eurl)
                    elif name:
                        return HTTPFound(location=eurl)
                    elif code:
                        return HTTPFound(location=eurl)
                    else:
                        return HTTPFound(location=eurl)

            # build redirect URL
            if name and code:
                rurl = request.route_url('admin_day_search', day=oday, name=name, code=code, _anchor=anchor, _query=query)
            elif name:
                rurl = request.route_url('admin_day_search_n', day=oday, name=name, _anchor=anchor, _query=query)
            elif code:
                rurl = request.route_url('admin_day_search_c', day=oday, code=code, _anchor=anchor, _query=query)
            else:
                rurl = request.route_url('admin_day_list', day=oday, _anchor=anchor, _query=query)
            # If add Person:
            if 'form.add' in params:
                return HTTPFound(location=request.route_url("admin_person_session",
                    code=session.code, _query=(("came_from", eurl),)))
            # Redirect:
            return HTTPFound(location=rurl)


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
        rooms = DBSession.query(Room).all()

        if 'form.submitted' in params or 'form.remove' in params:
            if item.id is None:
                DBSession.add(item)

            self.setAttrIfChanged(item, 'day', self.parseEnum, DayType)
            self.setAttrIfChanged(item, 'sessiontype', self.parseEnum, SessionType)

            self.setAttrIfChanged(item, 'code')
            self.setAttrIfChanged(item, 'title')

            self.setAttrIfChanged(item, 'facilitiesReq')
            self.setAttrIfChanged(item, 'facilitiesGot')

            self.setAttrIfChanged(item, 'room', self.parseCLSid, Room)
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

        return dict(section="session", item=item, came_from="",rooms=rooms, settings=self.settings)

    @view_config(route_name='admin_person_new', renderer='admin_person_edit.mako', permission='checkin')
    @view_config(route_name='admin_person_edit', renderer='admin_person_edit.mako', permission='checkin')
    @view_config(route_name='admin_person_session', renderer='admin_person_edit.mako', permission='checkin')
    def admin_person_edit(self):
        request = self.request
        params = request.params
        code = self.request.matchdict.get("code")
        next = params.get("came_from")

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
                print("\nADDING TO: %s" % sesscode)
                session = None
                if sesscode: session = DBSession.query(Session).filter(Session.code == sesscode).first()
                print("SEARCH RES: %s" % session)
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
            if next:
                return HTTPFound(location=next)
            return HTTPFound(location=request.route_url('admin_person_edit', id=item.id))

        return dict(section="person", item=item, came_from=next, code=code,)

    @view_config(route_name='admin_room_new', renderer='admin_location_edit.mako', permission='checkin')
    @view_config(route_name='admin_room_edit', renderer='admin_location_edit.mako', permission='checkin')
    def admin_location_edit(self):
        request = self.request
        params = request.params

        item = self.getItemOrCreate(Room)

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
                item.set_password(params["password"])

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
    def admin_view(self):
        return dict(section="admin", settings=DBSession.query(Settings).first(),
            timecodes=DBSession.query(TimeCode))

    @view_config(route_name='admin_timecode_delete', permission='superadmin')
    def admin_timecode_delete(self):
        item = self.getItemOrFail(TimeCode, self.request.matchdict.get("id"))
        DBSession.delete(item)
        return HTTPFound(location = self.request.route_url('admin_admin'))
    @view_config(route_name='admin_timecode_new', permission='superadmin')
    def admin_timecode_new(self):
        t = TimeCode(prefix=self.request.params.get("codePrefix"),
            time=self.request.params.get("time"),
            day=self.parseEnum("day", DayType))
        DBSession.add(t)
        return HTTPFound(location = self.request.route_url('admin_admin'))
    @view_config(route_name='nuke', renderer='nuke.mako', permission='admin')
    def nuke_view(self): return dict(section="admin")

    @view_config(route_name='nuke_go', permission='admin')
    def nuke_go_view(self):
        from transaction import commit
        meta = Base.metadata
        for table in reversed(meta.sorted_tables):
            if table.name == "user": continue
            elif table.name == "settings": continue
            elif table.name == "timecode": continue
            print('Clear table %s' % table)
            DBSession.execute(table.delete())
        commit()
        self.request.session.flash('Deleted all entries.')
        return HTTPFound(location = self.request.route_url('admin_admin'))

    @view_config(route_name='settings', permission='admin')
    def settings_save(self):
        params = self.request.params
        evals = 1 if params.get("evals") else 0
        handouts = 1 if params.get("handouts") else 0
        helpers = 1 if params.get("helpers") else 0
        #self.request.params.get()
        DBSession.query(Settings).update({"evals": evals, "handouts": handouts, "helpers": helpers})
        return HTTPFound(location = self.request.route_url('admin_admin'))

    @view_config(route_name='upload', permission='admin')
    def upload_view(self):
        from transaction import commit, abort

        request = self.request
        f = request.params['csvfile']
        t = request.params['uploadtype']
        if f == "":
            request.session.flash('No file selected.')
            return HTTPFound(location = request.route_url('admin_admin'))
        if t == "":
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
                if t == "sessionlocs":
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
                elif t == "handouts":
                    if not self.processHandouts(row):
                        abort()
                        request.session.flash("Failure from processHanouts")
                        return HTTPFound(location = request.route_url('admin_admin'))
                elif t == "cancelled":
                    if not self.processCancellations(row):
                        abort()
                        request.session.flash("Failure from processCancellations")
                        return HTTPFound(location = request.route_url('admin_admin'))

            request.session.flash('Upload of (%s) complete.' % filename)
        except UnicodeDecodeError:
            request.session.flash("Could not read (%s) correctly. Please upload as 'CSV UTF-8 (Comma Delimited) .csv'" % filename)
            unlink(input_file)
            abort()
        unlink(input_file)
        commit()
        return HTTPFound(location = request.route_url('admin_admin'))

    def processSession(self, row):
        cancelled = False
        params = self.request.params
        codecol = int(params.get("code"))
        titlecol = int(params.get("title")) if params.get("title", None) is not None else None
        sessiontypecol = params.get("sessiontype")
        numregcol = params.get("numreg")
        capacitycol = params.get("capacity")
        buildnumcol = int(params.get("buildnum"))
        sportsopts = params.getall("sports")
        #print(params)
        if not codecol:
            self.request.session.flash("Code and title column not selected after CSV.")
            return False

        if row[codecol].startswith("UNAVAILABLE "):
            row[codecol] = row[codecol][12:]
            cancelled = True
        elif row[codecol].startswith("CANCELLED "):
            row[codecol] = row[codecol][10:]
            cancelled = True
        c = row[codecol][0:4]
        # match code format:
        m = CODE.match(c)
        if m:
            c = m.group()
        else: c = None

        if not cancelled: room = self.processLocation(row)
        else: room = None
        if room is None:
            cancelled = True

        session = None
        if not c: return True # eject if non-code
        if c in self.sessions:
            session = self.sessions[c]
        else:
            session = DBSession.query(Session).filter(Session.code == c).first()

        # process title
        title = row[titlecol] if titlecol is not None else None
        if title:
            match = CODE_PREFIX.match(title) # remove code if in title
            if match:
                title = title[match.span()[1]:].strip()
        if cancelled:
            if title is not None: title = "CANCELLED " + title
            elif session is not None: title = "CANCELLED " + session.title
        timecode = returnTime(DBSession.query(TimeCode).all(),c)
        day = timecode.day
        time = timecode.time
        sport = False
        if row[buildnumcol].strip() in sportsopts:
            sport = True
        if session == None:
            # Create session
            session = Session(code=c, title=title, sessiontype=SessionType.NA,
                day=DayType(day), evaluations=HandoutType.At_Desk,
                room=room, cancelled=cancelled, time=time, sport=sport)
            DBSession.add(session)
            self.sessions[c] = session
        # update values/set
        if numregcol and row[int(numregcol)].strip():
            session.booked = row[int(numregcol)].strip()
        if capacitycol and row[int(capacitycol)].strip():
            session.max = row[int(capacitycol)].strip()
        session.room = room
        session.cancelled = cancelled
        session.day = day
        if titlecol is not None: session.title = title
        session.time = time
        session.sport = sport
        return True
    def processLocation(self, row):
        # Create room
        params = self.request.params
        buildnocol = int(params.get("buildnum"))
        buildnamecol = int(params.get("buildname"))
        roomcol = int(params.get("room"))
        capacitycol = params.get("capacity")
        capacity = row[int(capacitycol)].strip() if capacitycol else None
        buildno = row[buildnocol].strip()
        buildname = row[buildnamecol].strip()
        room = row[roomcol].strip()
        if room == "CANCELLED" or room.startswith("CANCELLED"):
            return None
        r = None
        if room in self.rooms:
            r = self.rooms[room]
        else:
            r = DBSession.query(Room).filter(Room.name == room).first()
        if r is None:
            r = Room(name=room)
            self.rooms[room] = r
        if capacity: r.capacity = capacity

        b = None
        if buildno in self.buildings:
            b = self.buildings[buildno]
        else:
            b = DBSession.query(Building).filter(Building.number == buildno).first()
        if b is None:
            b = Building(number=buildno, name=buildname)
            DBSession.add(b)
            self.buildings[buildno] = b
        r.building = b
        DBSession.add(b)
        DBSession.add(r)
        return r

    def processCancellations(self, row):
        # check if venue is CANCELLED
        params = self.request.params
        codecol = int(params.get("code"))
        buildnocol = int(params.get("buildnum"))
        buildnamecol = int(params.get("buildname"))
        venuecol = int(params.get("venue"))
        room = row[venuecol].strip()
        cancelled = True if room.startswith("CANCELLED") else False
        if c:
            s = DBSession.query(Session).filter(Session.code == c).first()
            if s:
                if cancelled: s.cancelled = True
                else:
                    r = processLocation(self, row)
                    if r: s.room = r
                # day = "T" if c[0] in ("A", "B", "C") else "F"
                # s = Session(code=c, title="Cancelled", sessiontype=SessionType.NA,
                #     day=DayType(day), evaluations=HandoutType.At_Desk,
                #     cancelled=True)
                # DBSession.add(s)
        return True;

    def processPerson(self, row):
        # TODO: add check for data of presenter "type"
        # TODO: make some of these options (int conversion will error if not there)
        params = self.request.params
        print(params)
        codecols = [int(x) for x in params.getall("sessioncode")]
        firstnamecol = int(params.get("firstname"))
        lastnamecol = int(params.get("lastname"))
        emailcol = int(params.get("email"))
        regidcol = int(params.get("regid"))
        phonecols = (int(x) for x in params.getall("phone"))
        orgcol = int(params.get("org"))
        shirtcol = int(params.get("shirt"))
        shirtopts = params.getall("shirtopts")

        # presenter filter
        presqualcol = int(params.get("presqual")) if params.get("presqual","") != "" else None
        if presqualcol is not None:
            presqualopts = params.getall("presopts")
            if row[presqualcol] not in presqualopts: return True

        #print(f"\n\nCODE: {codecols} \n\nREGID: {regidcol}\n")
        # if not codecols or regidcol:
        #     self.request.session.flash("Code and regid column not selected after CSV.")
        #     return False
        # Create or get Person | prefer using reg_id... TODO: add a fallback.

        firstname = row[firstnamecol].strip()
        lastname = row[lastnamecol].strip()
        email = row[emailcol].strip()
        phone = (row[x].strip() for x in phonecols)
        org = row[orgcol].strip()
        shirt = True if row[shirtcol].strip() in shirtopts else False
        p = None
        regid = row[regidcol].strip()
        if regid in self.people:
            p = self.people[regid]
        else:
            # lookup in database
            p = DBSession.query(Person).filter(Person.regid == regid).first()
        if p is None:
            # create
            p = Person(firstname=firstname, lastname=lastname, email=email,
                phone="\n".join(phone), organisation=org, regid=regid)
            self.people[regid] = p
            DBSession.add(p)
            DBSession.flush()
        p.shirt = shirt
        p.firstname = firstname
        p.lastname = lastname
        p.email = email
        p.phone = "\n".join(phone)
        p.org = org
        # process codes
        for x in codecols:
            sess = row[x].strip()
            # extract the code from the start. If no code, attempt to search for title.
            print(f"\nSESS: {sess}")
            m = CODE.match(sess)
            if m:
                print("MATCHED")
                c = m.group()
                self.addPersonToSession(p, c)
            else:
                if not sess.startswith("CANCELLED"):
                    print(f"ATTEMPTING TO SEARCH FOR: {sess}")
                    s = DBSession.query(Session).filter(Session.title == sess).first()
                    print(f"RESULT: {s}")
                    if s:
                        self.addPersonToSession(p, s.code)
        return True

    def processHost(self, row):
        # Create or get Person
        firstname = row[CSV_HOST_FNAME].strip()
        lastname = row[CSV_HOST_LNAME].strip()
        if not firstname or not lastname: return True

        email = row[CSV_HOST_EMAIL].strip()
        p = DBSession.query(Person).filter(Person.firstname == firstname,
            Person.lastname == lastname, Person.email == email).first()
        if not p:
            phone = []
            for ph in CSV_HOST_PHONE:
                if row[ph].strip(): phone.append(row[ph].strip())
            org = row[CSV_HOST_ORG].strip()
            p = Person(firstname=firstname, lastname=lastname, phone="\n".join(phone), email=email)
            DBSession.add(p)
            DBSession.flush()
        # Process their session
        for x in row[CSV_HOST_RNGS:CSV_HOST_RNGF]:
            x = x.strip()
            if not x: continue
            for match in CODE.findall(x):
                self.addPersonToSession(p, match[0] if match[0] else match[1], PersonType.Host)
        return True

    def processHandouts(self, row):
        # Skip non handout
        if not row[CSV_HAND_CODE].strip(): return True
        if not row[CSV_HAND_COPY].strip(): return True

        # Process the session
        session = row[0].strip()
        c = session[0:4]
        if CODE.match(c):
            c = CODE.match(c).group()
        else: c = None
        if c:
            s = DBSession.query(Session).filter(Session.code == c).one()
            s.handouts_said = HandoutSaidType.ACHPER_Copy
            if row[CSV_HAND_PRINT].strip():
                s.handouts = HandoutType.At_Desk
            else:
                s.handouts = HandoutType.NA
        return True

    def processSessionCaps(self, row):
        # Skip non row
        if not row[0].strip(): return True
        # Process the session
        session = row[0].strip()
        cancelled = False
        if session.startswith("UNAVAILABLE"):
            cancelled = True
            session = session[11:].strip()
        c = session[0:4]
        if CODE.match(c):
            c = CODE.match(c).group()
        else: c = None
        if not c and cancelled: self.request.session.flash("Cancelled non-session? {0}".format(row[0]))
        if c:
            day = "T" if c[0] in ("A", "B", "C") else "F"
            s = DBSession.query(Session).filter(Session.code == c).first()
            if s and cancelled:
                self.request.session.flash("CANSESS {0}?".format(c))
                s.cancelled = cancelled
            if not s and cancelled:
                self.request.session.flash("AddCan {0}".format(c))
                s = Session(code=c, title=session.split(":", 1)[1].strip(), sessiontype=SessionType.NA,
                    day=DayType(day), evaluations=HandoutType.NA,
                    cancelled=cancelled)
                DBSession.add(s)
            if not s and not cancelled:
                self.request.session.flash("NEW?? {0}".format(c))
                s = Session(code=c, title=session.split(":", 1)[1].strip(), sessiontype=SessionType.NA,
                    day=DayType(day), evaluations=HandoutType.NA,
                    cancelled=cancelled)
                DBSession.add(s)
            s.booked = int(row[CSV_CAPS_BOOKED] if row[CSV_CAPS_BOOKED] else 0)
            s.max = int(row[CSV_CAPS_MAX] if row[CSV_CAPS_MAX] else 0)
        return True

    def addPersonToSession(self, p, code, t=PersonType.Presenter):
        try:
            s = DBSession.query(Session).filter(Session.code == code).one()
            if not DBSession.query(Association).filter(Association.person_id == p.id, Association.session_id == s.id).first():
                DBSession.add(Association(person_id=p.id, session_id=s.id, type=t))
            else:
                DBSession.delete(DBSession.query(Association).filter(Association.person_id == p.id, Association.session_id == s.id).first())
                DBSession.flush()
                DBSession.add(Association(person_id=p.id, session_id=s.id, type=t))
                self.request.session.flash("{0}->{1}{2}".format(p.id, s.id, t.value))
                print("ALREADY ASSOCIATION (%s) for (%s, %s)" % (code, p.firstname, p.lastname))
        except NoResultFound:
            self.request.session.flash("x{0}->{1}{2}".format(p.id, code, t.value))
            print("\n\nCould not find Session: (%s)\n\n" % code)

    @view_config(route_name='nopresenter', renderer='csv', permission='admin')
    def nopresenter(self):
        #Really bad and slow and not optimal
        # select all sessions not cancelled
        nopres = []
        sessions = DBSession.query(Session).filter(Session.cancelled == False).all()
        for s in sessions:
            pres = 0
            for a in s.assoc:
                if a.type == PersonType.Presenter: pres += 1
            if pres < 1: nopres.append(s)

        header = ["CODE", "Name"]
        rows = (
            (
                item.code,
                item.title
            )
            for item in nopres
        )
        return dict(header=header, rows=rows)

    @view_config(route_name='test', renderer='test.mako', permission='admin')
    def test(self):
        return dict()


class SplashView(BaseAdminView):
    @view_config(route_name='admin_home', renderer='admin_home.mako', permission='splash')
    def home(self):
        return dict(section="home",)
