from datetime import timedelta
from time import time
from tempfile import NamedTemporaryFile
from shutil import copyfileobj

from unicodecsv import reader

from io import open as iopen, TextIOWrapper, BufferedRandom
from re import compile as recompile

CODE = recompile("([A-G][0-4][0-9])|(FP[0-1][0-9])")
CODE_PREFIX = recompile("([A-F][0-4][0-9]):|(FP[0-1][0-9]):")
# A01 A03 D39 E40 FP01 FP10 F10 F01 Z01 A50
# F1P0 FP30
# Feature Presentations // Thursday 8:45 - 10:00am
# Elective Session A // Thursday 10:45 - 12:15pm
TIME = recompile("[0-9]:[0-5][0-9][ap]m")

CODE_TIMEMAP = {
 "A" : ("Thursday", "10:50 - 11:50AM"),
 "B" : ("Thursday", "1:10 - 2:10PM"),
 "C" : ("Thursday", "2:20 - 3:20PM"),
 "D" : ("Friday", "9:00 - 10:00AM"),
 "E" : ("Friday", "10:50 - 11:50PM"),
 "F" : ("Friday", "1:10 - 2:10PM"),
 "FP" : ("Thursday", "9:00 - 10:00am"),
 "FP06" : ("Thursday", "8:45 - 10:00am"),
}
def returnTime(timelist, code):
    longest = None
    for timecode in timelist:
        if code.startswith(timecode.prefix):
            if longest is None or len(longest.prefix) < len(timecode.prefix):
                longest = timecode
    return longest

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
