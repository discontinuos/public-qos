import threading
import datetime
import os

from Environment import Environment
from Worker import Worker
from Codes import Codes
from Test import Test
from Maintenance import Maintenance
from Mirrors import Mirrors
from UrlMonitors import UrlMonitors

class Process:
    Mocking = False
    ForceMirrorUpdate = False
    ForceMonitorsUpdate = False

    def Run(self):
        # inicia el entorno
        environment = Environment()
        environment.Mocking = self.Mocking

        try:
            if environment.hasUrlMonitors():
                urlmonitors = UrlMonitors(environment)
                if environment.isMonitorsUpdateTime() or not os.path.exists(urlmonitors.getConfigFilename()) or self.ForceMonitorsUpdate:
                    urlmonitors.Get() 

            q = environment.LoadQueue()
            totalItems = q.qsize()

            if totalItems > 0:
                googlePing = Test.CreateConnectionTest()
                resTest = googlePing.Run(environment)
                environment.ConnectionAvailable = (resTest == Codes.R_200_OK or resTest == Codes.R_405_METHOD_NOT_ALLOWED)

                # procesa
                Worker.AppendFinalizerItems(q, environment)
                Worker.RunWorkers(environment, q)

                # se fija si quedaron cosas sin procesar para reflejarlo como error.
                remaining = Worker.EmptyQueue(q)
        
                if (remaining > 0):
                    environment.Output.LogError(str(q.qsize()) + " items no pudieron ser procesados.")

                summary = str(environment.TotalSucess.Value) + "/" + str(environment.TotalSucess.Value + environment.TotalFailed.Value) + " OK. "
                m = Mirrors(environment)
                m.UpdateMirrors(self.ForceMirrorUpdate)

                summary += str(environment.ElapsedTimeMs) + "ms. Micro: " + str(int(environment.getMicroTime() * 1000)) + "ms."

                environment.Output.Log(summary)
                environment.Output.Print(summary)
        except Exception as e:
            environment.Output.LogError('Se produjo un error: ' + str(e) + ".")

        Maintenance.UpdateVersionLocal()
