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
	"Presenter" : PersonType.presenter,
	"Co-Presenter" : PersonType.copresenter,
	"Contact Person Only" : PersonType.other,
	"Submitter Only" : PersonType.other
}

# room : () Re addr, Facs
BUILDING_MAP = {
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
	def __init__(self, firstname="", lastname=""):
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
	
def processFacsCell(data):
	data = data.replace(", ", "\n")
	data = data.replace(",", "\n")
	n = []
	for cell in sorted(data.split("\n")):
		cell.strip()
		if cell: n.append(cell)
	return n

def processFacsCells(cells):
	n = []
	for cell in cells:
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

# ["FIRSTNAME", "LASTNAME", "EMAIL", "ORG", "EMAIL"]
# ["NAME", "ORG", "EMAIL", "PHONE"]
def processCoPresent(cells, headers, type=None):
	#first, last, org, email
	#people = []
	#~ fgroup = [x.strip() for x in cells[0].split("/")]
	#~ lgroup = [x.strip() for x in cells[1].split("/")]
	#~ if len(fgroup) != len(lgroup):
		#~ print "WARNING: Multi CoPresent split len not match for\n(%s)\n(%s)" % (fgroup, lgroup)
		#~ return []
	if len(cells) != len(headers):
		print "WARNING: Headers don't match with cells."
		return None
#	org = cells[2].strip()
	p = TempPerson()
	for i, header in enumerate(headers):
		if header == "FIRSTNAME": p.firstname = cells[i].strip()
		if header == "LASTNAME": p.lastname = cells[i].strip()
		if header == "EMAIL": p.email.add(cells[i].strip())
		if header == "NAME":
			try:
				p.firstname, p.lastname = cells[i].strip().split(" ", 1)
			except:
				print "AAA: %r" % cells
				raise
	#~ people.append(p)
	p.type = type
	return p
		
def process(fn):
	names = {} # { (first, last) : TempPerson}
	sessions = {} # { code : TempSession }

	count = 1
	with codopen(fn, 'rb', 'utf-8') as csvfile:
		for row in unicode_csv_reader(csvfile):
			if row[0].strip() == 'SubmissionID': continue
			# CHECK ROW[10] OVER
			name = (u"%s" % row[7].strip(), u"%s" % row[8].strip())
			
			type = PRESTYPEMAP.get("Presenter", PersonType.other)
			
			#code = processCode(row[0].strip(), row[1].strip())
			code = row[1].strip()
			if "CANCELLED" in code: continue
			if not code: continue
			for code in code.split("&"):
				code = code.strip()
				
				title = row[4].strip()
				
				building = row[3].strip()
				if not building: building = "1"
				room = row[2].strip()
				#loctype = str(row[35].strip())
				sessname = row[4].strip()
				day = "T" if code[0] in ("A", "B", "C") else "F"
				
				phone = str(row[10].strip())
				
				org = row[8].strip()
				email = str(row[9].strip().lower())
				
				facilities_req = "\n".join(processFacsCells(row[47:54]))
				try: 
					if "&" in room:
						troom = room.split("&",1)[0].strip()
						facilities_got = BUILDING_MAP[troom][2]
						address = BUILDING_MAP[troom][0]
						loctype = BUILDING_MAP[troom][1]
					else:
						facilities_got = BUILDING_MAP[room][2]
						address = BUILDING_MAP[room][0]
						loctype = BUILDING_MAP[room][1]
				except:
					print "AAA: %r" % row
					print "KEYS: %r" % BUILDING_MAP.keys()
					raise
				#facilities_got = ["?"]
				#equipment = processEquip(row[36])
				#handouts_said, handouts_did = processHandouts(row[43:45])
				handouts_said = HANDOUTS[row[56].strip()]
				#handouts = handouts_did
				
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
				#s.location = location
				s.loctype = loctype
				s.address = address
				s.building = building
				s.room = room
				s.handouts_said = handouts_said
				s.handouts = None
				s.facilities_req = facilities_req if facilities_req else None
				s.facilities_got = facilities_got if facilities_got else None
				
				copres = []
				# process co-presenters part1
				if row[64].strip():
					if p and row[64].strip() != p.firstname:
						copres.append(processCoPresent(row[64:69], ["FIRSTNAME", "LASTNAME", "EMAIL", "ORG", "EMAIL"], 
							type=PRESTYPEMAP.get(row[70].strip(), PersonType.other))) #first, last, email, org, email again
				# process co-presenters part2
				if row[13].strip():
					copres.append(processCoPresent(row[13:17], ["NAME", "ORG", "EMAIL", "PHONE"], type=PersonType.copresenter))
				# process co-presenters part2 cont...
				if row[18].strip():
					copres.append(processCoPresent(row[18:22], ["NAME", "ORG", "EMAIL", "PHONE"], type=PersonType.copresenter))
				# process co-presenters part2 cont again...
				if row[23].strip():
					copres.append(processCoPresent(row[23:27], ["NAME", "ORG", "EMAIL", "PHONE"], type=PersonType.copresenter))
				# process co-presenters part2 cont again again...
				if row[28].strip():
					copres.append(processCoPresent(row[28:32], ["NAME", "ORG", "EMAIL", "PHONE"], type=PersonType.copresenter))

				for ip in copres:
					name = (ip.firstname, ip.lastname)
					oip = ip
					if name not in names:
						names[name] = ip
					else:
						ip = names[name]
					exists = False
					for session in ip.sessions:
						if code in session:
							exists = True
							break
					if exists: continue
					ip.sessions.append((code, oip.type))
						
				count += 1
		
	return (names, sessions)
	
def pootInDB(names, sessions, DBSession):
	dbsessionmap = {}
	
	with transaction.manager:
		# add sessions to DB then people
		for session in sessions:
			session = sessions[session]
			#~ if "online" in session.handouts.lower():
				#~ handouts = HandoutType.online
			#~ elif "received" in session.handouts.lower():
				#~ handouts = HandoutType.pending
			#~ else:
			handouts = HandoutType.na
				
			s = Session(code=session.code, title=session.name, 
				day=DayType.from_string(session.day), building=session.building, room=session.room,
				loctype=session.loctype, address=session.address, facilities_req=session.facilities_req,
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
				#t = PRESTYPEMAP[type]
				s = dbsessionmap[code]
				DBSession.add(Association(person_id=p.id, session_id=s.id,
					type=type))

def buildfacs(rows):
	facs = []
	if rows[0].strip(): facs.append("Data Projector")
	if rows[2].strip(): facs.append("Computer+DVD")
	elif rows[1].strip(): facs.append("Computer")
	if rows[3].strip(): facs.append("Doc Camera")
	if rows[4].strip(): facs.append("DVD/VCR")
	if rows[5].strip(): facs.append("Overhead Projector")
	if rows[8].strip(): facs.append("Whiteboard")
	if rows[9].strip(): facs.append("Projector screen")
	return "\n".join(facs)
	

def processBuildings(fn):
	with codopen(fn, 'rb', 'utf-8') as csvfile:
		for row in unicode_csv_reader(csvfile):
			BUILDING_MAP[row[0].strip()] = (row[2].strip(), row[3].strip(), buildfacs(row[4:15])) # addr, type, facs
	
def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <config_uri> <file to import.csv> [venueinfo.csv]\n'
		  '(example: "%s development.ini database.csv [venues.csv]")' % (cmd, cmd))
	sys.exit(1)
	
def main(argv=sys.argv):
	if len(argv) != 3 and len(argv) != 4:
		usage(argv)
	config_uri = argv[1]
	importfn = argv[2]
	if len(argv) == 4: bldfn = argv[3]
	else: bldfn = None
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	Base.metadata.create_all(engine)
	
	if bldfn: processBuildings(bldfn)
	names, sessions = process(importfn)
	pootInDB(names, sessions, DBSession)
	
if __name__ == "__main__": main()