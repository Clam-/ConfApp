from sqlalchemy import (
	Column,
	Boolean,
	Integer,
	ForeignKey,
	String,
	Index,
	Unicode,
	UnicodeText,
	Table,
	DateTime,
	)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import (
	declarative_base, 
	declared_attr
	)

from sqlalchemy.orm import (
	scoped_session,
	sessionmaker,
	relationship,
	deferred,
	backref,
	synonym,
	)

from zope.sqlalchemy import ZopeTransactionExtension

from cryptacular.bcrypt import BCRYPTPasswordManager

from pyramid.security import (
	Allow,
	Everyone,
	Authenticated,
	ALL_PERMISSIONS,
	)

from confapp.libs.declenum import DeclEnum

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class Base(object):
	"""Base class which provides common things."""
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()
	id = Column(Integer, primary_key=True)
	
	def __repr__(self):
		attrs = []
		for key in self._repr_attrs:
			attrs.append((key, getattr(self, key)))
		return self.__class__.__name__ + '(' + ', '.join(x[0] + '=' +
			repr(x[1]) for x in attrs) + ')'
	
Base = declarative_base(cls=Base)

class PrefDayType(DeclEnum):
	thursday = "T", "Thursday"
	friday = "F", "Friday"
	either = "E", "Either"
	
class DayType(DeclEnum):
	thursday = "T", "Thursday"
	friday = "F", "Friday"

FRIENDLYDAYMAP = {
	"thursday" : DayType.thursday,
	"friday" : DayType.friday,
}

class PersonType(DeclEnum):
	host = "H", "HOST"
	presenter = "P", "Presenter"
	copresenter = "C", "CoPresent"
	other = "O", "Other"
	submitter = "S", "Submitter"
	
class PersonTitle(DeclEnum):
	mr = "m", "Mr"
	mrs = "r", "Mrs"
	ms = "s", "Ms"
	miss = "i", "Miss"
	dr = "d", "Dr"
	prof = "p", "Prof"
	aprof = "a", "A/Prof"

class HandoutType(DeclEnum):
	na = "N", "N/A"
	pending = "P", "At Desk"
	handedout = "H", "Handed out"
	collected = "C", "Returned"
	online = "O", "Online-Only"

class HandoutSaidType(DeclEnum):
	na = "N", "N/A"
	pending = "A", "ACHPER to copy"
	handedout = "W", "Self provide"
	
class UserRole(DeclEnum):
	superadmin = "Z", "Super Admin"
	main = "M", "Main Check-in"
	sports = "S", "Sports Check-in"
	admin = "A", "Backend Admin"
	none = "N", "None"
	
class SessionType(DeclEnum):
	lecture = "L", "Lecture"
	workshopprac = "X", "Workshop - Practical"
	workshop = "W", "Workshop"
	practical = "P", "Practical"
	na = "N", "N/A"

class AudienceType(DeclEnum):
	pri = "P", "Primary"
	sec = "S", "Secondary"
	f10 = "F", "F-10"
	vce = "V", "VCE"
	
class FocusArea(DeclEnum):
	hpeh = "H", "HPE; Health Strand"
	hpem = "M", "HPE; Movement Strand"
	sport = "S", "Sport"
	outed = "O", "Outdoor Education"
	ict = "I", "ICT in HPE"
	vcepe = "V", "VCE Physical Education"
	vcehhd = "D", "VCE Health and Human Development"
	vceoes = "E", "VCE Outdoor and Environmental Studies"
	vcevet = "T", "VCE VET Sport and Recreation"
	

def sortstripstring(s):
	if not s: return s
	items = [item.strip() for item in s.split(",")]
	items.sort()
	return ",".join(items)

# Borrowed some snippets from https://github.com/Pylons/shootout/blob/master/shootout/models.py
crypt = BCRYPTPasswordManager()
def hash_password(password):
	return crypt.encode(password)

class User(Base):
	username = Column(Unicode(20), unique=True)
	name = Column(Unicode(50))
	_password = Column('password', String(60))
	
	def _get_password(self):
		return self._password
	def _set_password(self, password):
		self._password = hash_password(password)
	password = property(_get_password, _set_password)
	password = synonym('_password', descriptor=password)
	
	lastseen = Column(DateTime, nullable=True)
	role = Column(UserRole.db_type(), default=UserRole.none, nullable=False)

	@classmethod
	def get_by_username(cls, username):
		return DBSession.query(cls).filter(cls.username == username).first()
	@classmethod
	def check_password(cls, username, password):
		user = cls.get_by_username(username)
		if not user: return False
		if not user.password: return False
		return crypt.check(user.password, password)
		
	def label(self):
		return "User: %s" % (self.username)
		
class Person(Base):	
	lastname = Column(Unicode(100))
	firstname = Column(Unicode(100))
	organisation = Column(Unicode)
	
	phone = Column(String(100))
	email = Column(String(100))
	
	twitter = Column(String(20))
	bio = Column(Unicode)
	
	shirt = Column(Boolean)
	shirtcollect = Column(Boolean)
	shirtsize = Column(String(30))
	
	assoc = relationship("Association", backref="person", cascade="save-update, merge, delete")
	
	_repr_attrs = ["firstname", "lastname"]
	
	def label(self):
		return "Person: %s %s" % (self.firstname, self.lastname)
		
#person<->session association
class Association(Base):
	id = None
	person_id = Column(Integer, ForeignKey('person.id'), primary_key=True, autoincrement=False)
	session_id = Column(Integer, ForeignKey('session.id'), primary_key=True)
	type = Column(PersonType.db_type(), nullable=False)
	registered = Column(Boolean)
	registered_sport = Column(Boolean)
	#person = relationship("Person", backref="assoc")
	__table_args__ = (Index('idx_assoc', "session_id", "person_id"), )
	
	_repr_attrs = ["person_id", "session_id"]

class Session(Base):
	code = Column(Unicode(10), index=True, unique=True, nullable=True)
	cancelled = Column(Boolean, index=True)
	title = Column(Unicode(100))
	
	submissionID = Column(Integer)
	
	day = Column(DayType.db_type(), nullable=True, index=True)
	
	daypref = Column(PrefDayType.db_type())
	abstract = Column(Unicode)
	
	sessiontype = Column(SessionType.db_type(), nullable=False)
	keyaudience = relationship("SessionAudience", cascade="save-update, merge, delete")
	focusareas = relationship("SessionFocusArea", cascade="save-update, merge, delete")
	
	commercial = Column(Boolean, default=False)
	
	_facilities_req = deferred(Column(UnicodeText))
	_facilities_got = deferred(Column(UnicodeText))
	
	handouts = Column(HandoutType.db_type(), nullable=False, default=HandoutType.na)
	handouts_said = Column(HandoutSaidType.db_type(), nullable=False, default=HandoutSaidType.na)
	evaluations = Column(HandoutType.db_type(), nullable=False, default=HandoutType.pending)
	
	_equipment = Column(String(50))
	_equip_returned = Column(String(50))
	
	other = Column(Unicode(200))
	comments = Column(Unicode(200))
	
	booked = Column(Integer)
	max = Column(Integer)
	
	room_id = Column(Integer, ForeignKey('room.id'))
	room = relationship("Room", backref=backref('sessions', order_by=code), lazy='joined')
	
	_repr_attrs = ["code", "title"]
	
	assoc = relationship("Association", backref="session", cascade="save-update, merge, delete")
	
	def __init__(self, **kwargs):
		self.handouts = HandoutType.na
		self.handouts_said = HandoutSaidType.na
		self.evaluations = HandoutType.na
		for key in kwargs:
			setattr(self, key, kwargs[key])
	
	def label(self):
		return "Session: %s - %s" % (self.code, self.title[:20])
		
	@property
	def facilities_req(self):
		return self._facilities_req if self._facilities_req else ""
	@facilities_req.setter
	def facilities_req(self, value):
		if value: self._facilities_req = value
		else: self._facilities_req = None
	
	@property
	def facilities_got(self):
		return self._facilities_got if self._facilities_got else ""
	@facilities_got.setter
	def facilities_got(self, value):
		if value: self._facilities_got = value
		else: self._facilities_got = None
		
	@property
	def equipment(self):
		if self._equipment is None: return ""
		return self._equipment
	@equipment.setter
	def equipment(self, value):
		#sort and stuff
		self._equipment = sortstripstring(value)
		
	@property
	def equip_returned(self):
		if self._equip_returned is None: return ""
		return self._equip_returned
	@equip_returned.setter
	def equip_returned(self, value):
		#sort and stuff
		self._equip_returned = sortstripstring(value)

class SessionAudience(Base):
	session_id = Column(Integer, ForeignKey('session.id'))
	audience = Column(AudienceType.db_type())
	
class SessionFocusArea(Base):
	session_id = Column(Integer, ForeignKey('session.id'))
	focusarea = Column(FocusArea.db_type())

class Building(Base):
	name = Column(String(50))
	number = Column(String(20))
	address = Column(String(100))
	
	rooms = relationship("Room", backref="building", lazy='joined')

class Room(Base):
	name = Column(String(50))
	room = Column(String(20))
	capacity = Column(Integer)
	
	building_id = Column(Integer, ForeignKey('building.id'))

class Helper(Base):
	lastname = Column(Unicode(100))
	firstname = Column(Unicode(100))
	
	phone = Column(String(100))
	
	dispatched = Column(Integer)
	returned = Column(Integer)
	
	away = Column(Boolean)
	comment = Column(Unicode(50))
	
	session_id = Column(Integer, ForeignKey('session.id'))
	session = relationship("Session")
	__table_args__ = (Index('idx_helper', "away", "dispatched", "firstname"), )
	
	_repr_attrs = ["firstname", "lastname"]
	
	def label(self):
		return "Helper: %s %s" % (self.firstname, self.lastname)

class TripLogger(Base):
	helper_id = Column(Integer, ForeignKey('helper.id'))
	session_id = Column(Integer, ForeignKey('session.id'))
	code = Column(Unicode(3))
	building = Column(Unicode(5))
	time_departed = Column(Integer)
	time_returned = Column(Integer)
	time_total = Column(Integer)
	
class DeleteLogger(Base):
	item = Column(Unicode)
	timestamp = Column(DateTime)
	
CLASSMAPPER = {
	Person.__tablename__ : Person,
	Session.__tablename__ : Session,
	Helper.__tablename__ : Helper,
	User.__tablename__ : User,
}
#Index('idx_name1', "session.day", "person.lastname", "person.firstname")
#Index('idx_name2', "session.day", "person.firstname", "person.lastname")
#Index('idx_code', "session.day", "session.code")
#Index('idx_assoc', "session_id", "person_id")
#Index('idx_equip', "entry.equipment", "entry.equip_returned")

class RootFactory(object):
	__acl__ = [
		(Allow, UserRole.superadmin, ALL_PERMISSIONS),
		(Allow, UserRole.admin, 'admin'),
		(Allow, Authenticated, 'checkin'),
		(Allow, Everyone, 'splash'),
		# COMMENT OUT THE BELOW POST TESTING
		#~ (Allow, Everyone, 'admin'),
		#~ (Allow, Everyone, 'checkin'),
	]
	def __init__(self, request):
		self.request = request


def decenumReverseMap(t, s, debug=False):
	for x in t:
		if debug: print repr(x.description), repr(s)
		if x.description == s:
			return x

