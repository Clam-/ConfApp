from datetime import timedelta
from time import time
from tempfile import NamedTemporaryFile
from shutil import copyfileobj

from unicodecsv import reader

from io import open as iopen, TextIOWrapper, BufferedRandom
from re import compile as recompile

CODE = recompile("[A-Z][0-3][0-9]")
CODE2 = recompile("FP[0-1][0-9]")
# Feature Presentations // Thursday 8:45 - 10:00am
# Elective Session A // Thursday 10:45 - 12:15pm
TIME = recompile("[0-9]:[0-5][0-9][ap]m")

CODE_TIMEMAP = {
 "A" : "10:45 - 12:15pm",
 "B" : "1:15 - 2:45pm",
 "C" : "3:00 - 4:30pm",
 "D" : "8:45 - 10:15am",
 "E" : "11:45 - 1:15pm",
 "F" : "2:00 - 3:30pm",
 "FP01" : "8:45 - 10:00am",
 "FP02" : "8:45 - 10:00am",
 "FP03" : "8:45 - 10:00am",
 "FP04" : "8:45 - 10:00am",
 "FP05" : "8:45 - 10:00am",
 "FP06" : "10:45 - 11:45am",
 "FP07" : "10:45 - 11:45am",
 "FP08" : "10:45 - 11:45am",
 "FP09" : "10:45 - 11:45am",
 "FP10" : "10:45 - 11:45am",
}

CSV_VENUE_CODE = 0
CSV_VENUE_TITLE = 1
CSV_VENUE_ADDR = 4
CSV_VENUE_BUILDING = 0
CSV_VENUE_LOC = 2
CSV_VENUE_ROOM = 2
CSV_VENUE_NAME = 1
CSV_PEOPLE_FNAME = 9
CSV_PEOPLE_LNAME = 10
CSV_PEOPLE_ORG = 14
CSV_PEOPLE_ORGOTHER = 15
CSV_PEOPLE_RNGS = 32
CSV_PEOPLE_RNGF = 39 # last col +1 for slicing.
CSV_PEOPLE_PHONE = (12, 13)
CSV_PEOPLE_EMAIL = 11
CSV_PEOPLE_SHIRT = 2
CSV_PEOPLE_SHIRTM = ("Complimentary Speaker", "Complimentary Registration")
CSV_CAPS_CODE = 0
CSV_CAPS_BOOKED = 1
CSV_CAPS_MAX = 2
CSV_HOST_FNAME = 1
CSV_HOST_LNAME = 2
CSV_HOST_EMAIL = 3
CSV_HOST_PHONE = (4,5)
CSV_HOST_ORG = 6
CSV_HOST_RNGS = 10
CSV_HOST_RNGF = 17 # last col +1 for slicing.

def read_csv(fname):
	with open(fname, "rb") as f:
		for row in reader(f, encoding="utf-8"):
			yield row


def convertfile(fp):
	f = NamedTemporaryFile(delete=False)
	fp.seek(0)
	copyfileobj(fp, f)
	return f.name


#distance_of_time_in_words delta=seconds
def distance_of_time_in_words(delta):
	#print(delta)
	hours, minutes, seconds = delta//3600, (delta//60)%60, delta % 60

	if hours:
		min = (minutes/60)*10
		if min > 1:
			return "%d.%dh" % (hours, min)
		else:
			return "%dh" % hours
	elif minutes:
		sec = (seconds/60)*10
		if sec > 2:
			return "%d.%dm" % (minutes, sec)
		else:
			return "%dm" % minutes
	else:
		return "%ds" % seconds
