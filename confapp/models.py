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


def sortstripstring(s):
	if not s: return s
	items = [item.strip() for item in s.split(",")]
	items.sort()
	return ",".join(items)

sessper_assoc_table = Table('sess_per_assoc', Base.metadata,
	Column('session_id', Integer, ForeignKey('session.id')),
	Column('person_id', Integer, ForeignKey('person.id'))
)

class Person(Base):
	typename = "Person"
	routetype = "person"
	
	lastname = Column(Unicode(100))
	firstname = Column(Unicode(100))
	
	phone = Column(String(100))
	email = Column(String(100))

class Association(Base):
	id = None
	person_id = Column(Integer, ForeignKey('person.id'), primary_key=True)
	session_id = Column(Integer, ForeignKey('session.id'), primary_key=True)
	type = Column(PersonType.db_type(), nullable=False)
	registered = Column(Boolean)
	person = relationship("Person", backref="assoc")


class Session(Base):
	typename = "Session"
	routetype = "session"
	
	code = Column(Unicode(10), index=True, unique=True)
	title = Column(Unicode(50))
	
	day = Column(DayType.db_type(), nullable=False, index=True)
	
	location = Column(String(40))
	loctype = Column(String(40))
	
	_facilities = deferred(Column(UnicodeText))
	
	handouts = Column(HandoutType.db_type(), nullable=False)
	evaluations = Column(HandoutType.db_type(), nullable=False)
	
	_equipment = Column(String(50))
	_equip_returned = Column(String(50))
	
	other = Column(Unicode(200))
	comments = Column(Unicode(200))
	
	assoc = relationship("Association", backref="session")
	
	@property
	def facilities(self):
		return self._facilities if self._facilities else ""
	@facilities.setter
	def facilities(self, value):
		if value: self._facilities = value
		else: self._facilities = None
		
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

Index('idx_name1', "session.day", "person.lastname", "person.firstname")
Index('idx_name2', "session.day", "person.firstname", "person.lastname")
Index('idx_code', "session.day", "session.code")
#Index('idx_equip', "entry.equipment", "entry.equip_returned")

