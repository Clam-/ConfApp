from csv import reader
import csv
from codecs import open as codopen

import os
import sys
import transaction

from sqlalchemy import engine_from_config

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

PRESTYPEMAP = {
	"PRESENTER" : PersonType.presenter,
	"COPRESENTER" : PersonType.copresenter,
	"Contact Person Only" : PersonType.other,
	"NOT A COPRESENTER" : PersonType.other
}

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

class TempPerson:
	def __init__(self, firstname, lastname):
		self.firstname = firstname
		self.lastname = lastname
		self.email = set()
		self.phone = set()
		self.sessions = [] #code, type

class TempSession:
	def __init__(self, code, day):
		self.code = code
		#self.name = set()
		#self.locations = set()
		#self.loctypes = set()
		self.day = day
		#self.handouts = set()
		
HANDOUTS = {
	"I will require ACHPER Victorian Branch to photocopy my handout materials" : "A",
	"I will provide my own handout materials and distribute to delegates" : "W",
	"I will not be providing handouts" : "N",
	"" : "N",
}

def processHandouts(cells):
	said = HANDOUTS[cells[0].strip()]
	did = cells[1].strip().lower()
	return said, did

def processCode(code, ap):
	if ap:
		return "%s-%s" % (code, ap)
	else:
		return code

def processEquip(data):
	pass # map long names to short names, like "Whiteboard" : "WB"
		
def processRoom(cells):
	if "Monash Sports" in cells[0]:
		cells[0] = "1"
	return str("%s.%s" % (cells[0].strip(), cells[1].strip()))
	
def processFacs(data):
	data = data.replace(", ", "\n")
	data = data.replace(",", "\n")
	n = []
	for cell in sorted(data.split("\n")):
		cell.strip()
		if cell: n.append(cell)
	return n

def processPhone(p1, p2):
	if p1 and p2:
		return (p1, p2)
	elif p1:
		return (p1,)
	elif p2:
		return (p2,)
	else:
		return ()
		
def processCoPresent(cells):
	#first, last, org, email
	people = []
	fgroup = [x.strip() for x in cells[0].split("/")]
	lgroup = [x.strip() for x in cells[1].split("/")]
	if len(fgroup) != len(lgroup):
		print "WARNING: Multi CoPresent split len not match for\n(%s)\n(%s)" % (fgroup, lgroup)
		return []
	org = cells[2].strip()
	if len(cells) >= 4:
		email = cells[3].strip()
	else:
		email = ""
	for i, fname in enumerate(fgroup):
		p = TempPerson(fname, lgroup[i])
		p.email.add(email)
		p.org = org
		people.append(p)
	return people
		
def process(fn):
	names = {} # { (first, last) : TempPerson}
	sessions = {} # { code : TempSession }

	count = 1
	with codopen(fn, 'rb', 'utf-8') as csvfile:
		for row in unicode_csv_reader(csvfile):
			if row[0].strip() == 'CODE': continue
			# CHECK ROW[10] OVER
			name = ("%s" % row[6].strip(), "%s" % row[7].strip())
			
			type = "PRESENTER"
			
			#code = processCode(row[0].strip(), row[1].strip())
			code = row[0]
			
			sessname = row[4].strip()
			
			location = processRoom(row[39:41])
			loctype = str(row[35].strip())
			
			day = "T" if code[0] in ("A", "B", "C") else "F"
			
			phone = str(row[10].strip())
			
			org = row[8].strip()
			email = str(row[9].strip().lower())
			
			facilities_req = "\n".join(processFacs(row[36]))
			facilities_got = "\n".join(processFacs(row[37]))
			
			#equipment = processEquip(row[36])
			
			handouts_said, handouts_did = processHandouts(row[43:45])
			handouts = handouts_did
			
			p = None
			if name != ("", ""):
				if name in names:
					p = names[name]
				else:
					p = TempPerson(*name)
					names[name] = p
					
				p.email.add(email)
				#~ for ph in phone:
				p.phone.add(phone)
				
				p.sessions.append((code, type))
				
			s = None
			if code in sessions:
				s = sessions[code]
			else:
				s = TempSession(code, day)
				sessions[code] = s
				
			s.name = sessname
			s.location = location
			s.loctype = loctype
			s.handouts_said = handouts_said
			s.handouts = handouts
			s.facilities_req = facilities_req if facilities_req else None
			s.facilities_got = facilities_got if facilities_got else None
			
			copres = []
			# process co-presenters part1
			if row[12].strip():
				copres += processCoPresent(row[12:16]) #first, last, org, email
			# process co-presenters part2
			if row[17].strip():
				copres += processCoPresent(row[17:20])
			
			for ip in copres:
				name = (ip.firstname, ip.lastname)
				if name not in names:
					names[name] = ip
				else:
					ip = names[name]
				type = "COPRESENTER"
				ip.sessions.append((code, type))
					
			count += 1
		
	return (names, sessions)
	
def pootInDB(names, sessions, DBSession):
	dbsessionmap = {}
	
	with transaction.manager:
		# add sessions to DB then people
		for session in sessions:
			session = sessions[session]
			if "online" in session.handouts.lower():
				handouts = HandoutType.online
			elif "received" in session.handouts.lower():
				handouts = HandoutType.pending
			else:
				handouts = HandoutType.na
				
			s = Session(code=session.code, title=session.name, 
				day=DayType.from_string(session.day), location=session.location,
				loctype=session.loctype, facilities_req=session.facilities_req,
				facilities_got=session.facilities_got, handouts_said=HandoutSaidType.from_string(session.handouts_said),
				handouts=handouts, evaluations=HandoutType.pending)
			DBSession.add(s)
			dbsessionmap[session.code] = s
		
		for person in names:
			person = names[person]
			p = Person(lastname=person.lastname, firstname=person.firstname,
				phone="\n".join(person.phone), email="\n".join(person.email))
			DBSession.add(p)
			DBSession.flush()
			for code, type in person.sessions:
				t = PRESTYPEMAP[type]
				s = dbsessionmap[code]
				DBSession.add(Association(person_id=p.id, session_id=s.id,
					type=t))
			
	
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
	
	names, sessions = process(importfn)
	pootInDB(names, sessions, DBSession)
	
if __name__ == "__main__": main()