from unicodecsv import writer
from io import BytesIO

class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        fout = BytesIO()
        cw = writer(fout, encoding='utf-8')

        cw.writerow(value['header'])
        cw.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="report.csv"'
        return fout.getvalue()
