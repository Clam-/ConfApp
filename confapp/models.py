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
	)

from zope.sqlalchemy import ZopeTransactionExtension

from confapp.libs.declenum import DeclEnum

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class Base(object):
	"""Base class which provides common things."""
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()
	id = Column(Integer, primary_key=True)
	
Base = declarative_base(cls=Base)

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

class HandoutType(DeclEnum):
	na = "N", "N/A"
	pending = "P", "Pending"
	handedout = "H", "Handed out"
	collected = "C", "Collected"

class HandoutSaidType(DeclEnum):
	na = "N", "N/A"
	pending = "A", "ACHPER to copy"
	handedout = "W", "Self provide"

def sortstripstring(s):
	if not s: return s
	items = [item.strip() for item in s.split(",")]
	items.sort()
	return ",".join(items)

class Person(Base):
	typename = "Person"
	routetype = "person"
	
	lastname = Column(Unicode(100))
	firstname = Column(Unicode(100))
	
	phone = Column(String(100))
	email = Column(String(100))

#person<->session association
class Association(Base):
	id = None
	person_id = Column(Integer, ForeignKey('person.id'), primary_key=True)
	session_id = Column(Integer, ForeignKey('session.id'), primary_key=True)
	type = Column(PersonType.db_type(), nullable=False)
	registered = Column(Boolean)
	person = relationship("Person", backref="assoc")
	__table_args__ = (Index('idx_assoc', "session_id", "person_id"), )


class Session(Base):
	typename = "Session"
	routetype = "session"
	
	code = Column(Unicode(10), index=True, unique=True)
	title = Column(Unicode(50))
	
	day = Column(DayType.db_type(), nullable=False, index=True)
	
	location = Column(String(40))
	loctype = Column(String(40))
	
	_facilities_req = deferred(Column(UnicodeText))
	_facilities_got = deferred(Column(UnicodeText))
	
	handouts = Column(HandoutType.db_type(), nullable=False)
	handouts_said = Column(HandoutSaidType.db_type(), nullable=False)
	evaluations = Column(HandoutType.db_type(), nullable=False)
	
	_equipment = Column(String(50))
	_equip_returned = Column(String(50))
	
	other = Column(Unicode(200))
	comments = Column(Unicode(200))
	
	assoc = relationship("Association", backref="session")
	
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
		return self._equipment
	@equipment.setter
	def equipment(self, value):
		#sort and stuff
		self._equipment = sortstripstring(value)
		
	@property
	def equip_returned(self):
		return self._equip_returned
	@equip_returned.setter
	def equip_returned(self, value):
		#sort and stuff
		self._equip_returned = sortstripstring(value)


class Helper(Base):
	typename = "Helper"
	routetype = "helper"
	
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

class TripLogger(Base):
	helper_id = Column(Integer, ForeignKey('helper.id'))
	session_id = Column(Integer, ForeignKey('session.id'))
	code = Column(Unicode(3))
	building = Column(Unicode(5))
	time_departed = Column(Integer)
	time_returned = Column(Integer)
	time_total = Column(Integer)
	

#Index('idx_name1', "session.day", "person.lastname", "person.firstname")
#Index('idx_name2', "session.day", "person.firstname", "person.lastname")
#Index('idx_code', "session.day", "session.code")
#Index('idx_assoc', "session_id", "person_id")
#Index('idx_equip', "entry.equipment", "entry.equip_returned")

