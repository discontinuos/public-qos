import os
import datetime

from Codes import Codes 
from Environment import Environment

class Summary:
    Success = 0
    MonthdaysSummary = {}
    GlobalSummary = {}
    HoursSummary = {}
    WeekdaysSummary = {}
    Monitors = []
    From = datetime.datetime(year = 2900, month = 1, day = 1)
    To = datetime.datetime(year = 1900, month = 1, day = 1)

    def __init__ (self, source):
        self.source = source
        self.target = os.path.splitext(source)[0]+'-summary.txt'
        self.Initialize(self.GlobalSummary, ['Totales'])
        self.Initialize(self.HoursSummary, range(0, 24))
        self.Initialize(self.WeekdaysSummary, range(1, 8))
        self.Initialize(self.MonthdaysSummary, range(1, 32))

    def Increment(self, result, ms, ownerMonitor, startTime, interval):
        if startTime < self.From:
           self.From = startTime
        if startTime > self.To:
           self.To = startTime
        if not ownerMonitor in self.Monitors:
            self.Monitors.append(ownerMonitor)
        self.IncrementDiccionary(self.GlobalSummary, 'Totales', result, ms, interval)
        self.IncrementDiccionary(self.HoursSummary, startTime.hour, result, ms, interval)
        self.IncrementDiccionary(self.WeekdaysSummary, startTime.weekday() + 1, result, ms, interval)
        self.IncrementDiccionary(self.MonthdaysSummary, startTime.day, result, ms, interval)
        
    def IncrementDiccionary(self, dict, key, result, ms, interval):
        current = dict[key]
        # success
        if result == Codes.R_200_OK:
            current['success'] += 1
            current['minuteSuccess'] += interval
            current['totalMs'] += ms
        elif result == Codes.R_OFFLINE:
            current['noconnection'] += 1
            current['minuteNoconnection'] += interval
        else:
            current['errors'] += 1
            current['minuteErrors'] += interval 
        dict[key] = current

    def Initialize(self, arr, range):
        for i in range: 
            arr[i] = { 'success' : 0, 'errors': 0, 'noconnection': 0, 'totalMs' : 0, 'minuteSuccess' : 0, 'minuteErrors' : 0, 'minuteNoconnection' : 0 }

    def Save(self):
        # Genera el nombre de archivo
        f = open(self.target, 'w+')
        print(Environment.APP_TITLE + '\n', file=f)
        print('Monitores:'.ljust(12) + str(self.Monitors), file=f)
        print('Período:'.ljust(12) + str(self.From) + ' al ' + str(self.To), file=f)
        self.writeDiccionary(f, self.GlobalSummary, 'Resumen')
        self.writeDiccionary(f, self.HoursSummary, 'Horas del día')
        self.writeDiccionary(f, self.WeekdaysSummary, 'Días de la semana')
        self.writeDiccionary(f, self.MonthdaysSummary, 'Días del mes')
        f.close()

    def writeDiccionary(self, file, dict, title):
        print('', file=file)
        LABELS_WIDTH = 17
        COLS_WIDTH = 7
        print("=" * (len(dict) * COLS_WIDTH + LABELS_WIDTH), file=file)
        print(title.upper(), file=file)
        
        header = ''.ljust(LABELS_WIDTH )
        for key in dict:
            header += str(key).center(COLS_WIDTH)
        print(header, file=file)

        print(" " * LABELS_WIDTH + "-" * (len(dict) * COLS_WIDTH), file=file)

        line = 'Uptime (%)'.ljust(LABELS_WIDTH )
        for key, value in dict.items():
            line += str(self.percentageProportion(value['minuteSuccess'], value['minuteErrors'])).center(COLS_WIDTH)
        print(line, file=file)

        line = 'Downtime (mins.)'.ljust(LABELS_WIDTH )
        for key, value in dict.items():
            line += str(value['minuteErrors'] if value['errors'] + value['success'] > 0 else '').center(COLS_WIDTH)
        print(line, file=file)

        line = 'Latency (ms.)'.ljust(LABELS_WIDTH )
        for key, value in dict.items():
            line += str(self.average(value['totalMs'], value['success'])).center(COLS_WIDTH)
        print(line, file=file)

        line = 'Coverage (%)'.ljust(LABELS_WIDTH )
        for key, value in dict.items():
            line += str(self.percentageProportion(value['minuteSuccess']+value['minuteErrors'], value['minuteNoconnection'])).center(COLS_WIDTH)
        print(line, file=file)
        
        line = 'Samples'.ljust(LABELS_WIDTH )
        for key, value in dict.items():
            line += str(self.nonZero(value['success']+value['errors'])).center(COLS_WIDTH)
        print(line, file=file)
        
        print("=" * (len(dict) * COLS_WIDTH + LABELS_WIDTH), file=file)

    def percentageProportion(self, p1, p2):
        if (p1 + p2 == 0):
            return ""
        else:
            return str(int(p1 * 10000 / (p1 + p2)) / 100) + "%"

    def average(self, p1, p2):
        if (p2 == 0):
            return ""
        else:
            return int(p1 / p2)

    def nonZero(self, p1):
        if (p1 == 0):
            return ""
        else:
            return p1