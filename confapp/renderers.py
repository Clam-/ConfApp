# http://stackoverflow.com/a/9981791
from csv import writer, QUOTE_ALL, excel
from cStringIO import StringIO
from codecs import getincrementalencoder

# https://docs.python.org/2/library/csv.html
class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""
	def __init__(self, f, dialect=excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = StringIO()
		self.writer = writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)
		
class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        fout = StringIO()
        writer = UnicodeWriter(fout, quoting=QUOTE_ALL)

        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="report.csv"'
        return fout.getvalue()