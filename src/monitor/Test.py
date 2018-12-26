import urllib.request
import datetime
import http

from urllib.parse import urlsplit
from urllib.error import URLError, HTTPError

from Codes import Codes 
from WebClient import WebClient

class Test:
    Url = ""
    Interval = 0
    Offset = 0
    Owner = ""
    Monitor = ""

    # Inicializes using the name of the config file
    def __init__ (self, owner, monitor, url, interval, offset):
        self.Url = url
        self.Interval = int(interval)
        self.Offset = int(offset)
        self.Monitor = monitor
        self.Owner = owner
    
    def MatchInterval(self, environment):
        return environment.MinuteInHour % self.Interval == self.Offset

    def Validate(self, environment):
        if self.Url == "":
            environment.Output.LogError("El monitor " + self.Owner + "-" + self.Monitor + " no tiene un valor definido para la Url.")
            return False
        if self.Interval != 60 and self.Interval != 30 and self.Interval != 20 and \
            self.Interval != 15 and self.Interval != 10  and self.Interval != 6 and \
            self.Interval != 5 and self.Interval != 2  and self.Interval != 1:
            environment.Output.LogError("El intervalo de " + self.Owner + "-" + self.Monitor + " no es un divisor de 60 (valor: " + str(self.Interval) + ").")
            return False
        if self.Offset < 0 or self.Offset >= self.Interval:
            environment.Output.LogError("El offset de " + self.Owner + "-" + self.Monitor + " debe ser positivo y menor al intervalo (valor: " + str(self.Offset) + ").")
            return False
        return True

    def Run(self, environment):
        if not environment.ConnectionAvailable:
            result = Codes.R_OFFLINE
            environment.Output.Print("Sin conexión.")
            environment.Output.AppendResult(self, result, 0)
            return result

        start = datetime.datetime.now()
        timeout = environment.HTTP_TIMEOUT
        
        wc = WebClient()
        wc.Verbose = environment.Verbose
        ret = wc.Get(self.Url, timeout, 3)
        result = ret['result']

        diff = datetime.datetime.now() - start
        ms = int(diff.total_seconds() * 1000)

        if result == Codes.R_ERROR:
            environment.Output.LogError(ret['error_description'])

        if result == Codes.R_200_OK:
            environment.Output.Print('[' + self.Owner + "-" + self.Monitor + "] resuelto en " + str(ms) + "ms.")
        else:
            environment.Output.Print('[' + self.Owner + "-" + self.Monitor + "] falló en " + str(ms) + "ms. " + Codes.CodeToString(result))

        # Graba en el output
        environment.Output.AppendResult(self, result, ms)
        return result

    def CreateConnectionTest():
        ret = Test('Connection', 'Google', 'http://www.google.com', 1, 0)
        return ret
