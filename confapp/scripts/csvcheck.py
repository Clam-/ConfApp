from csv import reader
import csv
from codecs import open as codopen

import sys, os

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
		self.name = set()
		self.locations = set()
		self.loctypes = set()
		self.day = day
		self.handouts_did = set()
		self.handouts_said = set()
		self.facilities_req = set()
		self.facilities_got = set()

HANDOUTS = {
	"I will require ACHPER Victorian Branch to photocopy my handout materials" : "A",
	"I will provide my own handout materials and distribute to delegates" : "W",
	"I will not be providing handouts" : "n/a",
	"" : "n/a",
}

def processHandouts(cells):
	said = HANDOUTS[cells[0].strip()]
	did = cells[1].strip().lower() == "received"
	return said, did
		
def processRoom(cells):
	if "Monash Sports" in cells[0]:
		cells[0] = "1"
	return str("%s.%s" % (cells[0].strip(), cells[1].strip()))
	
def processFacs(data):
	data = data.replace(", ", "\n")
	data = data.replace(",", "\n")
	n = []
	for cell in data.split("\n"):
		cell.strip()
		if cell: n.append(cell)
	return n

def processEquip(data):
	pass # map long names to short names, like "Whiteboard" : "WB"

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
	email = cells[3].strip()
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
			
			name = ("%s" % row[6].strip(), "%s" % row[7].strip())
			
			type = "PRESENTER"
			
			code = row[0]
			
			sessname = row[4].strip()
			
			location = processRoom(row[38:40])
			loctype = str(row[34].strip())
			
			day = "T" if code[0] in ("A", "B", "C") else "F"
			
			#phone = processPhone(str(row[24].strip()), str(row[25].strip()))
			
			org = row[8].strip()
			email = str(row[9].strip().lower())
			
			facilities_req = "\n".join(processFacs(row[35]))
			facilities_got = "\n".join(processFacs(row[36]))
			
			equipment = processEquip(row[36])
			
			handouts_said, handouts_did = processHandouts(row[42:44])
			
			p = None
			
			if name != ("", ""):
				if name in names:
					p = names[name]
				else:
					p = TempPerson(*name)
					names[name] = p
					
				p.email.add(email)
				#~ for ph in phone:
					#~ p.phone.add(ph)
				
				p.sessions.append((code, type))
			
			s = None
			if code in sessions:
				s = sessions[code]
			else:
				s = TempSession(code, day)
				sessions[code] = s
				
			s.name = sessname
			s.locations.add(location)
			s.loctypes.add(loctype)
			s.handouts_said.add(handouts_said)
			s.handouts_did.add(handouts_did)
			if facilities_req:
				s.facilities_req.add(facilities_req)
			if facilities_got:
				s.facilities_got.add(facilities_got)	
			count += 1
			
			copres = []
			# process co-presenters part1
			if row[11].strip():
				copres += processCoPresent(row[11:15]) #first, last, org, email
			# process co-presenters part2
			if row[15].strip():
				copres += processCoPresent(row[16:19])
			
			for ip in copres:
				name = (ip.firstname, ip.lastname)
				if name not in names:
					names[name] = ip
				else:
					ip = names[name]
				type = "COPRESENTER"
				ip.sessions.append((code, type))
						
		
	return (names, sessions)
	
			
	
def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <file to import.csv>\n'
		  '(example: "%s database.csv")' % (cmd, cmd))
	sys.exit(1)
	
def main(argv=sys.argv):
	if len(argv) != 2:
		usage(argv)
	importfn = argv[1]
	
	names, sessions = process(importfn)
	codes = set()
	for s in sessions:
		s = sessions[s]
		if len(s.locations) > 1:
			print "Too many locations for %s, %s" % (s.code, s.locations)
		if len(s.loctypes) > 1:
			print "Too many loctypes for %s, %s" % (s.code, s.loctypes)
		if len(s.handouts_did) > 1:
			print "Too many handouts_did for %s, %s" % (s.code, s.handouts_did)
		if len(s.handouts_said) > 1:
			print "Too many handouts_said for %s, %s" % (s.code, s.handouts_said)
		if len(s.facilities_req) > 1:
			print "Too many facilities_req for %s, %s" % (s.code, s.facilities_req)
		if len(s.facilities_got) > 1:
			print "Too many facilities_got for %s, %s" % (s.code, s.facilities_got)
		codes.add(s.code)
	
	sesspresenter = set()
	for p in names:
		p = names[p]
		for code, type in p.sessions: #code, type
			if type == "PRESENTER":
				sesspresenter.add(code)
	codes.difference_update(sesspresenter)
	print "NO PRESENTER FOR THE FOLLOWING: %s" % codes
	return names
	
if __name__ == "__main__": 
	main()