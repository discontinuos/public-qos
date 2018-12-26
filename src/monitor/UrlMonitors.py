import datetime
import configparser
import os
import csv
import io
import shutil
import http
import glob
import hashlib

from urllib.parse import urlsplit
import urllib.request

from urllib.error import URLError, HTTPError
from Environment import Environment
from WebClient import WebClient
from Codes import Codes

class UrlMonitors:
    def __init__(self, environment):
        self.environment = environment

    def getConfigFilename(self):
        return Environment.getMyFolder() + '/config/urlmonitors.ini'
                
    def Get(self):
        self.environment.Output.Print("Actualizando monitores...")
        data = self.environment.MONITORS_SOURCE_URL
        if data == "":
            return False
        login = self.environment.MONITORS_LOGIN_URL
        if login != "":
            # Autentica
            cookies = self.Authenticate(login)
            if cookies == None:
                return False
        else:
            cookies = None
        # trae los datos
        scsv = self.GetData(data, cookies)
        if not self.Validate(scsv):
            return
        
        filename = self.getConfigFilename() 
        n = self.csvToFile(scsv, filename)
        self.environment.Output.Log("Monitores actualizados: " + str(n) + " obtenidos.")
        return True

    def csvToFile(self, scsv, filename):
        reader_list = csv.DictReader(io.StringIO(scsv))
        header = next(reader_list)
        mons = open(filename, "w")
        n = 0
        while(True):
            row = next(reader_list, None)
            if row == None: break
            name = row['Nombre'].replace(" ", "")
            print('[' + name + "]", file=mons)
            print("Url=" + row['URL:URL'].strip().replace("%", "%%"), file=mons)
            if self.environment.DEFAULT_INTERVAL > 1:
                # genera el offset
                m = hashlib.md5()
                m.update(name.encode('utf-8'))
                h2 = m.digest()                
                offset = (self.environment.DEFAULT_OFFSET + h2[0]) % self.environment.DEFAULT_INTERVAL
                print("Offset=" + str(offset), file=mons)
            n += 1
        mons.close()
        return n

    def Validate(self, scsv):
        if scsv == None:
            self.environment.Output.LogError("Monitores fallaron al actualizar contenido (resultado vacío).")
            return False
        if scsv.startswith("Nombre,URL") == False:
            self.environment.Output.LogError("Monitores fallaron al actualizar contenido (no inicia con Nombre,URL).")
            return
        try:
            filename = self.getConfigFilename() + ".tmp"
            self.csvToFile(scsv, filename)
            monitors = configparser.ConfigParser()
            monitors.read(filename)
            os.remove(filename)
            for monitorName in monitors:
                if monitorName != "DEFAULT" and len(monitorName.split('-')) != 2:
                    raise Exception("Los nombres de monitores deben tener la forma owner-monitor (Inválido: " + monitorName + ").")
            return True
        except Exception as e:
            self.environment.Output.LogError('Monitores fallaron al actualizarse . Error: ' + str(e) + ".")
            return False

    def GetData(self, data, cookie):
        timeout= self.environment.HTTP_TIMEOUT
        wc = WebClient()
        wc.Verbose = self.environment.Verbose
        wc.Cookies = cookie
        wc.RandomAgent = False
        ret = wc.Get(data, timeout)
        result=ret['result']
        
        if result == Codes.R_200_OK:
            return ret['text']
        else:
            self.environment.Output.LogError('No fue posible actualizar los monitores: ' + data + '. Error: ' + Codes.CodeToString(result))
        return None

    def Authenticate(self, login):
        # Se fija si tiene parámetros de post en la url
        # en la forma #param1=value&param2=value
        url = urllib.parse.urlsplit(login)
        args = self.parsePostArgs(url.fragment)
        loginUrl = (login + "#").split("#")[0]
        timeout = self.environment.HTTP_TIMEOUT
        # Navega         
        wc = WebClient()
        wc.Verbose = self.environment.Verbose
        wc.RandomAgent = False
        if args == None: 
            ret = wc.Get(loginUrl, timeout, 0)
        else:
            ret = wc.Post(loginUrl, args, timeout)
        result = ret['result']
        # Listo
        if result == Codes.R_200_OK or result == Codes.R_302_NOT_FOUND:
            return ret['cookies']
        else:
            self.environment.Output.LogError('No fue posible identificarse para actualizar los monitores: ' + login + '. Error: ' + Codes.CodeToString(result))
        return None
    
    def parsePostArgs(self, fragment):
        formArgs = None
        if fragment == "": return

        formArgs = {}
        for item in fragment.split("&"):
            key, value = item.split("=")
            formArgs[key] = value
        
        return formArgs
        