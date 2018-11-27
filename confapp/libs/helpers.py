from datetime import timedelta
from time import time
from tempfile import NamedTemporaryFile
from shutil import copyfileobj

from backports.csv import reader
from io import open as iopen, TextIOWrapper, BufferedRandom
from re import compile as recompile

CODE = recompile("[A-Z][0-3][0-9]")
CODE2 = recompile("FP0[0-6]")


def read_csv(fname):
	with iopen(fname, newline='', encoding='utf-8-sig') as f:
		for row in reader(f):
			yield row


def convertfile(fp):
	f = NamedTemporaryFile(delete=False)
	fp.seek(0)
	copyfileobj(fp, f)
	return f.name


#distance_of_time_in_words delta=seconds
def distance_of_time_in_words(delta):
	print delta
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