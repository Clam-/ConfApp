from csv import reader
import csv
from codecs import open as codopen

import sys, os

people = None

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
		self.handouts = set()
		self.facilities = set()
		
def processCode(code, ap):
	if ap:
		return "%s-%s" % (code, ap)
	else:
		return code
		
def processRoom(cells):
	return str("%s.%s" % (cells[0].strip(), cells[1].strip()))
	
def processFacs(cells):
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
	
def process(fn):
	names = {} # { (first, last) : TempPerson}
	sessions = {} # { code : TempSession }

	count = 1
	with codopen(fn, 'rb', 'utf-8') as csvfile:
		for row in unicode_csv_reader(csvfile):
			if row[0].strip() == 'CODE': continue
			
			name = ("%s" % row[15].strip(), "%s" % row[16].strip())
			
			type = row[6].strip()
			
			code = processCode(row[0].strip(), row[1].strip())
			
			sessname = row[11].strip()
			
			location = processRoom(row[52:54])
			loctype = str(row[54].strip())
			
			day = "T" if code[0] in ("A", "B", "C") else "F"
			
			phone = processPhone(str(row[24].strip()), str(row[25].strip()))
			
			org = row[17].strip()
			email = str(row[18].strip().lower())
			
			facilities = "\n".join(processFacs(row[135:142]))
			
			handouts = True if row[153].strip() else False
			
			p = None
			if name in names:
				p = names[name]
			else:
				p = TempPerson(*name)
				names[name] = p
				
			p.email.add(email)
			for ph in phone:
				p.phone.add(ph)
			
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
			s.handouts.add(handouts)
			if facilities:
				s.facilities.add(facilities)
			count += 1
		
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
		if len(s.handouts) > 1:
			print "Too many handouts for %s, %s" % (s.code, s.handouts)
		if len(s.facilities) > 1:
			print "Too many facilities for %s, %s" % (s.code, s.facilities)
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
	people = main()