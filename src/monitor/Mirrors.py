import datetime
import configparser
import os
import shutil
import glob
import zipfile

from Functions import Functions
from Environment import Environment
from WebClient import WebClient

class Mirrors:
    servers = []
    zipPath = ''
    zipFile = None

    def __init__(self, environment):
        self.environment = environment
        self.zipPath = Environment.getMyFolder() + "/mirrors"
        
    def loadConfig(self):
        mirrors = configparser.ConfigParser()
        mirrors.read(self.getConfigFilename())
        return mirrors

    def getConfigFilename(self):
        return Environment.getMyFolder() + '/config/mirrors.ini'

    def AddMonitorToZip(self, mirror, owner, monitor, ):
        lastMonth = mirror['LastMonth']
        relativePath = owner + "/" + monitor 
        path = self.environment.getOutputFolder() + "/" + relativePath 
        if lastMonth == "":
            # lee todo
            months = ['']
        elif lastMonth == self.currMonth:
            # lee actual
            months = [self.currMonth]
        else:
            # lee desde lastMonth a actual 
            months = [lastMonth]
            current = lastMonth
            while(current != self.currMonth):
                current = self.NextMonth(current)
                months.append(current)

        for month in months:
            src_files = glob.glob(path + "/" + owner + "-" + monitor + "#" + month + "*.mon")
            if month != "": month += "#"
            for file_name in src_files:
                file = Functions.getFilenameNoExt(file_name) + "#" + self.environment.INSTANCE_ID + ".mon"
                parts = file.split('#')
                zip = self.getZipFile(mirror['Name'], parts[1])
                zip.write(file_name, self.environment.OUTPUT_FOLDER + "/" + relativePath + "/" + file)

    def NextMonth(self, current):
        year, month = current.split('-')
        month = int(month) + 1
        year = int(year)
        if month > 12:
            month = 1
            year+=1
        if (month < 10):
            return str(year) + "-0" + str(month)
        else:
            return str(year) + "-" + str(month)

    def UpdateMonth(self, mirror):
        with open(self.getConfigFilename()) as f:
            lines = f.read().splitlines()
        isInSection = False
        done = False
        for n in range(len(lines)):
            line = lines[n]
            if isInSection == True:
                if line.startswith("["):
                    lines[n] = "LastMonth=" + self.currMonth + "\n" + lines[n]
                    done = True
                    break
                if line.startswith("LastMonth="):
                    lines[n] = "LastMonth=" + self.currMonth
                    done = True
                    break
            elif line.startswith("[" + mirror['Name'] + "]"):
                isInSection = True
        if not done: lines.append("LastMonth=" + self.currMonth)

        if self.environment.Mocking: return

        w = open(self.getConfigFilename(), "w") 
        w.write('\n'.join(lines))
        w.close()

    def UpdateMirrors(self, forceUpdate = False):
        self.LoadMirrors(forceUpdate)
        self.currMonth = self.environment.YearMonth
        # para asegurar una secuencia consistente, primero armar el paquete...
        for mirror in self.servers:
            bytes = self.CreateZips(mirror)
            self.environment.Output.Print('Actualizando mirror '+ mirror['Name'] + " (" + str(int(bytes / 1024)) + "KBytes)...")
            
        # luego envía...
        for mirror in self.servers:
            if self.SendZips(mirror) and mirror['LastMonth'] != self.currMonth:
                self.UpdateMonth(mirror)

    def LoadMirrors(self, forceUpdate):
        mirrors = self.loadConfig()
        self.servers = []
        for mirrorName in mirrors.sections():
            mirror = mirrors[mirrorName]
            svr = { 'Name': mirrorName, 'Url': mirror.get('Url', ''), 'Frequency' : mirror.get('Frequency', 'Daily'), 'Key' : mirror.get('Key', ''), 'LastMonth' : mirror.get('LastMonth', '')}
            if svr['Url'] == "": 
                self.environment.Output.LogError("El mirror " + mirrorName + " no tiene un valor definido para Url.")
            elif svr['Key'] == "": 
                self.environment.Output.LogError("El mirror " + mirrorName + " no tiene un valor definido para Key.")
            elif svr['Frequency'] != "Daily" and svr['Frequency'] != "Weekly": 
                self.environment.Output.LogError("El mirror " + mirrorName + " no tiene un valor definido para Frequency.")
            else:
                frequency = svr['Frequency']
                if self.environment.isMirrorTime() or forceUpdate:
                    if svr['Frequency'] == 'Daily' or forceUpdate or (frequency == 'Weekly' and self.environment.isMirrorDay()):
                        self.servers.append(svr)

    def CreateZips(self, mirror):
        if not os.path.exists(self.zipPath):
            os.makedirs(self.zipPath)
        self.zipFiles = {}
        monitors = self.environment.GetMonitors()
        for monitorName in monitors:
            owner, monitor = monitorName.split('-')
            self.AddMonitorToZip(mirror, owner, monitor)
        # listo
        totalBytes = 0
        for key in self.zipFiles:
            file = self.zipFiles[key]
            # agrega configs
            for ini in ['config', 'monitors', 'urlmonitors']:
                filename = Environment.getMyFolder() + '/config/'+ini+'.ini'
                if os.path.exists(filename):
                    file.write(filename, "config/"+ini+"#" + self.environment.INSTANCE_ID + ".ini")
            file.close()
            totalBytes += os.path.getsize(file.filename)            
        return totalBytes

    def getZipFile(self, mirrorName, month):
        key = mirrorName + '#' + month
        if not key in self.zipFiles:
            path = self.zipPath + "/" + mirrorName
            if not os.path.exists(path):
                    os.makedirs(path)
            filename = path + "/" + month + "#" + self.environment.INSTANCE_ID + ".zip"
            if os.path.exists(filename):
                os.remove(filename)
            file = zipfile.ZipFile(filename, "w")
            self.zipFiles[key] = file
            self.appendLog(file, 'logs', month)
            self.appendLog(file, 'errors', month)
        return self.zipFiles[key]         

    def appendLog(self, zip, folder, month):
        # agrega logs
        logfile = self.environment.Output.getFilename(folder, month)
        if os.path.exists(logfile):
            zip.write(logfile, folder+"/"+month+"#" + self.environment.INSTANCE_ID + ".log")
                
    def SendZips(self, mirror):
        # solo falta esto, y que lo llame
        src_files = glob.glob(self.zipPath + "/" + mirror['Name'] + "/*.zip")
        wc = WebClient()
        wc.Verbose = self.environment.Verbose

        wc.RandomAgent = False
 
        for file_name in src_files:
            files = { "file": file_name }
            fileOnly = Functions.getFilename(file_name)
            params = {"command": 'put',
                       "key" : mirror['Key'],
                       "filename" : fileOnly,
                       "instanceId": self.environment.INSTANCE_ID }
            url = mirror['Url']
            if self.environment.Mocking == False:
                res = wc.PostFiles(url, params, files)
                if res['code'] != 200 or res['text'] != "OK":    
                    self.environment.Output.LogError('Mirroring falló. No fue posible navegar la URL: ' + url + '. Error: ' + res['msg'])
                    return False

        for file_name in src_files:
            os.remove(file_name)

        self.environment.Output.Log("Mirror actualizado: " +  mirror['Name'] + ".")
        return True
