from csv import reader
import csv
from codecs import open as codopen

import os
import sys
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from pyramid.paster import (
	get_appsettings,
	setup_logging,
	)

from confapp.models import (
	DBSession,
	Base,
	Person,
	Session,
	Association,
	DayType,
	HandoutType,
	PersonType,
	HandoutSaidType,
	FRIENDLYDAYMAP,
	)

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
	# csv.py doesn't do Unicode; encode temporarily as UTF-8:
	csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
							dialect=dialect, **kwargs)
	for row in csv_reader:
		# decode UTF-8 back to Unicode, cell by cell:
		yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')

def process(fn, DBSession):
	names = {} # { (first, last) : TempPerson}
	sessions = {} # { code : TempSession }

	count = 1
	with transaction.manager:
		with codopen(fn, 'rb', 'utf-8') as csvfile:
			type = "HOST"
			for row in unicode_csv_reader(csvfile):
				if row[0].strip() == 'Session': continue
				session = row[0].strip()
				for index, session in [(1, "D%.2d"), (2, "E%.2d"), (3, "F%.2d")]:
					if row[0]:
						code = session % int(row[0])
						name = row[index].strip()
						if name:
							firstname, lastname = name.split(" ",1)
							p = None
							try: p = DBSession.query(Person).filter(Person.firstname == firstname, Person.lastname == lastname).one()
							except NoResultFound:
								p = Person(lastname=lastname, firstname=firstname)
								DBSession.add(p)
								DBSession.flush()
							if not p:
								print "ERROR"
								sys.exit(1)
							s = DBSession.query(Session).filter(Session.code == code).one()
							DBSession.add(Association(person_id=p.id, session_id=s.id,
								type=PersonType.host))
	
def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <config_uri> <file to import.csv>\n'
		  '(example: "%s development.ini database.csv")' % (cmd, cmd))
	sys.exit(1)
	
def main(argv=sys.argv):
	if len(argv) != 3:
		usage(argv)
	config_uri = argv[1]
	importfn = argv[2]
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	Base.metadata.create_all(engine)
	
	process(importfn, DBSession)
	
if __name__ == "__main__": main()