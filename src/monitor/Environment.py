import time
import datetime
import configparser
import queue
import os

from Output import Output
from Counter import Counter
from Test import Test

class Environment:
    # Constantes
    MAX_SECONDS_PER_THREAD = 40
    APP_TITLE = "DUMB MONITOR v1"

    # Atributes
    Output = None
    WORKER_THREADS = 0
    HTTP_TIMEOUT = 0
    MONITORS_LOGIN_URL = ""
    MONITORS_SOURCE_URL = ""
    GMT = 0
    OUTPUT_FOLDER = ""
    DEFAULT_INTERVAL = 0
    INSTANCE_ID = ""
    DEFAULT_OFFSET = 0
    ConnectionAvailable = True
    startTime = 0
    PrintToScreen = False
    Verbose = False
    processorTime = 0

    Mocking = False

    TotalSucess = Counter()
    TotalFailed = Counter()

    # Constructor
    def __init__(self):
        self.processorTime = time.process_time()
        self.Output = Output(self)
        config = configparser.ConfigParser()
        config.read(Environment.getMyFolder() + '/config/config.ini')
        self.PrintToScreen = config['Processor'].get('PrintToScreen', 'False') == "True"
        self.DEFAULT_OFFSET = int(config['Monitors']['DefaultMinutesOffset'])
        self.MONITORS_LOGIN_URL = config['Monitors'].get('LoginUrl', '')
        self.MONITORS_SOURCE_URL = config['Monitors'].get('SourceUrl', '')
        self.DEFAULT_INTERVAL = int(config['Monitors']['DefaultMinutesInterval'])
        self.GMT = int(config['Monitors']['GMT'])
        self.INSTANCE_ID = config['Mirrors']['InstanceId']
        self.WORKER_THREADS = int(config['Processor']['MaxThreads'])
        self.OUTPUT_FOLDER = 'results'
        self.HTTP_TIMEOUT = int(config['Monitors']['HttpSecondsConnectionTimeout'])
        self.startTime = self.now()
        if (self.HTTP_TIMEOUT > 30):
            raise Exception("El Timeout no puede ser mayor a 30 segundos.")
        return

	# Execution elapsed time indicator
    def getElapsedTimeMs(self):
        return int((self.now() - self.startTime).total_seconds() * 1000)          
        
    def getMicroTime(self):
        return time.process_time() - self.processorTime
           
    def now(self):
        return datetime.datetime.utcnow() + datetime.timedelta(hours = self.GMT)
        
    def isMirrorTime(self):
        return self.startTime.hour == 0 and self.startTime.minute == 0

    def isMirrorDay(self):
        return WeekDay == 6
    
    def isMonitorsUpdateTime(self):
        return (self.startTime.hour % 6 == 0) and self.startTime.minute == 0

    def hasUrlMonitors(self):
        return self.MONITORS_SOURCE_URL != ""

    def getMyFolder():
        return os.path.dirname(os.path.abspath(__file__))
    def getMyFolderLocal(self):
        return Environment.getMyFolder()

    def getOutputFolder(self):
        return Environment.getMyFolder() + "/" + self.OUTPUT_FOLDER

    def GetMonitors(self):
        monitors = self.getLocalMonitors()
        monitors.update(self.getUrlMonitors())
        return monitors

    def getLocalMonitors(self):
        return self.getFileMonitors('monitors.ini')
    def getUrlMonitors(self):
        return self.getFileMonitors('urlmonitors.ini')

    def getFileMonitors(self, file):
        filename = Environment.getMyFolder() + '/config/' + file 
        if not os.path.exists(filename):
            return {}
        monitors = configparser.ConfigParser()
        monitors.read(filename)
        ret = {}
        for monitorName in monitors:
            if monitorName != "DEFAULT":
                ret[monitorName] = monitors[monitorName]
        return ret

    def LoadQueue(self):
        # carga en la cola los tests a hacer
        monitors = self.GetMonitors()
        q = queue.Queue()
        skipped = 0
        for monitorName in monitors:
            test = self.CreateMonitor(monitorName, monitors[monitorName])
            if test.Validate(self):
                if test.MatchInterval(self):
                    q.put(test)
                else:
                    skipped += 1
        self.Output.Print("Cargados para procesar: " + str(q.qsize()) + ".")
        if skipped > 0:
            self.Output.Print("Omitidos por no aplicar offset: " + str(skipped) + ".")
            self.Output.Print("Minuto: " + str(self.MinuteInHour))
        return q

    def CreateMonitor(self, monitorName, monitor):
        parts = monitorName.split('-')
        test = Test(parts[0], parts[1], monitor.get('Url', ''), monitor.get('Interval', self.DEFAULT_INTERVAL), 
                    monitor.get('Offset', self.DEFAULT_OFFSET))
        return test

    def sliceInMonth(self, interval):
        return int(self.getMinuteInMonth() / interval)
    
    def getYearMonth(self):
        if (self.startTime.month < 10):
            return str(self.startTime.year) + "-0" + str(self.startTime.month)
        else:
            return str(self.startTime.year) + "-" + str(self.startTime.month)
        
    def getWeekDay(self):
        return self.startTime.weekday()

    def getMinuteInMonth(self):
        return (self.startTime.day - 1) * 1440 + self.startTime.hour * 60 + self.startTime.minute
    def getMinuteInHour(self):
        return self.startTime.minute
      
    ElapsedTimeMs = property(getElapsedTimeMs)
    YearMonth = property(getYearMonth)
    WeekDay = property(getWeekDay)
    MinuteInMonth = property(getMinuteInMonth)
    MinuteInHour = property(getMinuteInHour)
