from datetime import timedelta
from time import time

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