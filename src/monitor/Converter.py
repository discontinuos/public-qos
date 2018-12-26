import os
import datetime
import csv

from Codes import Codes 
from Summary import Summary
from Functions import Functions

class Converter:    
    def __init__ (self, source):
        self.source = source
        self.target = os.path.splitext(source)[0]+'.csv'

    def SaveCSV(self, target, append = False):
        self.Save(target, False, append)

    def Save(self, target = "", createSummary = True, append = False):
        if target == "":
            target = self.target
        if append:
            csvfile = open(target, 'a', newline='') 
        else:
            csvfile = open(target, 'w', newline='') 
        fieldnames = ['owner', 'monitor', 'instance', 'year', 'month', 'day', 'weekday(1=m)', 'hour', 'time', 'interval(mins)', 'success', 'responseMs', 'responseCode', 'responseStatus']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        if not append:
            writer.writeheader()
        summary = Summary(target)
        # Procesa el archivo
        self.ConvertFile(writer, summary, self.source)
        # Sale
        if createSummary:
            summary.Save()
        csvfile.close()
        return

    def ConvertFile(self, writer, summary, source):
        filename = Functions.getFilenameNoExt(source)

        parts = filename.split('#')
        ownerMonitor = parts[0]
        time = parts[1]
        intervals = parts[2]
        if len(parts) > 3:
            instance = parts[3]
        else:
            instance = 'local' 
        owner, monitor = ownerMonitor.split('-')
        year, month = time.split('-')
        interval, offset = intervals.split('-')

        row = {'owner': owner, 'monitor': monitor, 'instance' : instance, 'year': year, \
                'month': month, 'interval(mins)': interval }
        intervalMinutes = int(interval)
        offsetMinutes = int(offset)
        startTime = datetime.datetime(year=int(year), month=int(month), day=1)
        startTime += datetime.timedelta(minutes = offsetMinutes)
        sourcefile = open(self.source, mode='rb') 
        result = sourcefile.read(1)
        while (result != b""):
            lo = sourcefile.read(1)
            hi = sourcefile.read(1)
            result = result[0]
            ms = lo[0] + 256 * hi[0]
            if result != Codes.R_EMPTY:
                row['time'] = startTime;
                row['hour'] = startTime.hour;
                row['day'] = startTime.day;
                row['weekday(1=m)'] = startTime.weekday() + 1;
                summary.Increment(result, ms, ownerMonitor, startTime, intervalMinutes)
                if result != Codes.R_OFFLINE:
                    if result == Codes.R_200_OK:
                        row['success'] = 1
                    else:
                        row['success'] = 0
                    row['responseMs'] = ms
                else:
                    row['success'] = ''
                    row['responseMs'] = ''
                row['responseCode'] = result
                row['responseStatus'] = Codes.CodeToString(result)
                writer.writerow(row)
            startTime +=  datetime.timedelta(minutes = intervalMinutes)
            result = sourcefile.read(1)
        
        sourcefile.close()
        print('Procesado: ' + source)
        