from datetime import timedelta
from time import time
from tempfile import NamedTemporaryFile
from shutil import copyfileobj

from unicodecsv import reader

from io import open as iopen, TextIOWrapper, BufferedRandom
from re import compile as recompile

CODE = recompile("[A-Z][0-3][0-9]")
CODE2 = recompile("FP[0-1][0-9]")

CSV_VENUE_CODE = 0
CSV_VENUE_TITLE = 1
CSV_VENUE_ADDR = 4
CSV_VENUE_BUILDING = 1
CSV_VENUE_ROOM = 2
CSV_VENUE_ST = 0
CSV_PEOPLE_FNAME = 0
CSV_PEOPLE_LNAME = 1
CSV_PEOPLE_ORG = 2
CSV_PEOPLE_RNGS = 3
CSV_PEOPLE_RNGF = 8
CSV_PEOPLE_PHONE = (9, 10)
CSV_PEOPLE_EMAIL = 11
CSV_PEOPLE_SHIRT = 12
CSV_PEOPLE_SHIRTM = ("Complimentary Speaker", "Comp Speaker Day Reg", "Complimentary Registration")

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
