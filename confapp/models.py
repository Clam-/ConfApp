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
	BINARY,
	Enum,
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

from zope.sqlalchemy import register

import bcrypt

from pyramid.security import (
	Allow,
	Everyone,
	Authenticated,
	ALL_PERMISSIONS,
	)

from enum import Enum as pyEnum

DBSession = scoped_session(sessionmaker())
register(DBSession)

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

class PrefDayType(pyEnum):
	Thursday = "T"
	Friday = "F"
	Either = "E"

class DayType(pyEnum):
	Thursday = "T"
	Friday = "F"

class PersonType(pyEnum):
	Host = "H"
	Presenter = "P"
	CoPresent = "C"
	Other = "O"
	Submitter = "S"

class HandoutType(pyEnum):
	NA = "N"
	At_Desk = "P"
	Handed_out = "H"
	Returned = "C"
	Online_Only = "O"

class HandoutSaidType(pyEnum):
	NA = "N"
	ACHPER_Copy = "A"
	Self_Provide = "W"

class UserRole(pyEnum):
	SuperAdmin = "Z"
	Main_Checkin = "M"
	Sports_Checkin = "S"
	Admin = "A"
	none = "N"

class SessionType(pyEnum):
	Lecture = "L"
	Workshop_Prac = "X"
	Workshop = "W"
	Practical = "P"
	NA = "N"

class AudienceType(pyEnum):
	Primary = "P"
	Secondary = "S"
	F10 = "F"
	VCE = "V"

# class FocusArea(pyEnum):
# 	hpeh = "H", "HPE; Health Strand"
# 	hpem = "M", "HPE; Movement Strand"
# 	sport = "S", "Sport"
# 	outed = "O", "Outdoor Education"
# 	ict = "I", "ICT in HPE"
# 	vcepe = "V", "VCE Physical Education"
# 	vcehhd = "D", "VCE Health and Human Development"
# 	vceoes = "E", "VCE Outdoor and Environmental Studies"
# 	vcevet = "T", "VCE VET Sport and Recreation"


def sortstripstring(s):
	if not s: return s
	items = [item.strip() for item in s.split(",")]
	items.sort()
	return ",".join(items)

class User(Base):
	username = Column(Unicode(20), unique=True)
	name = Column(Unicode(50))
	password_hash = Column(BINARY(60))

	def set_password(self, pw):
		self.password_hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())

	def check_password(self, pw):
		if self.password_hash is not None:
			return bcrypt.checkpw(pw.encode('utf8'), self.password_hash)
		return False

	lastseen = Column(DateTime, nullable=True)
	role = Column(Enum(UserRole), nullable=False, name="role")

	@classmethod
	def get_by_username(cls, username):
		return DBSession.query(cls).filter(cls.username == username).first()
	@classmethod
	def check_user_pass(cls, username, password):
		user = cls.get_by_username(username)
		if not user: return False
		if not user.password_hash: return False
		return user.check_password(password)

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
	type = Column(Enum(PersonType), nullable=False, name="type")
	registered = Column(Boolean)
	registered_sport = Column(Boolean)
	#person = relationship("Person", backref="assoc")
	__table_args__ = (Index('idx_assoc', "session_id", "person_id"), )

	_repr_attrs = ["person_id", "session_id"]

class Session(Base):
	code = Column(Unicode(10), index=True, unique=True, nullable=True)
	cancelled = Column(Boolean, index=True)
	title = Column(Unicode(100))
	time = Column(Unicode(20))

	submissionID = Column(Integer)

	day = Column(Enum(DayType), nullable=False, name="day")

	daypref = Column(Enum(PrefDayType), name="daypref")
	abstract = Column(Unicode)

	sessiontype = Column(Enum(SessionType), nullable=False, name="sessiontype")
	# keyaudience = relationship("SessionAudience", cascade="save-update, merge, delete")
	# focusareas = relationship("SessionFocusArea", cascade="save-update, merge, delete")

	commercial = Column(Boolean, default=False)

	_facilities_req = deferred(Column(UnicodeText))
	_facilities_got = deferred(Column(UnicodeText))

	handouts = Column(Enum(HandoutType), nullable=False, name="handouts", default=HandoutType.NA)
	handouts_said = Column(Enum(HandoutSaidType), nullable=False, name="handouts_said", default=HandoutSaidType.NA)
	evaluations = Column(Enum(HandoutType), nullable=False, name="evaluations", default=HandoutType.At_Desk)

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
		self.handouts = HandoutType.NA
		self.handouts_said = HandoutSaidType.NA
		self.evaluations = HandoutType.NA
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

# class SessionAudience(Base):
# 	session_id = Column(Integer, ForeignKey('session.id'))
# 	audience = Column(Enum(AudienceType), name="audience")
#
# class SessionFocusArea(Base):
# 	session_id = Column(Integer, ForeignKey('session.id'))
# 	focusarea = Column(Enum(FocusArea), name="focusarea")

class Building(Base):
	name = Column(String(50))
	number = Column(String(20))
	address = Column(String(100))

	rooms = relationship("Room", backref="building", lazy='joined')

	def __str__(self):
		return "{0}".format(self.number)


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
		(Allow, UserRole.SuperAdmin, ALL_PERMISSIONS),
		(Allow, UserRole.Admin, 'admin'),
		(Allow, Authenticated, 'checkin'),
		(Allow, Everyone, 'splash'),
		# COMMENT OUT THE BELOW POST TESTING
		#~ (Allow, Everyone, 'admin'),
		#~ (Allow, Everyone, 'checkin'),
	]
	def __init__(self, request):
		self.request = request
