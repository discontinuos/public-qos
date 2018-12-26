import datetime
import os

from Codes import Codes 

class Output:
    # Constructor
    def __init__(self, environment):
        self.environment = environment
        return

    def AppendResult(self, test, result, ms):
        if result == Codes.R_200_OK:
            self.environment.TotalSucess.Increment()
        else:
            self.environment.TotalFailed.Increment()
        if self.environment.Mocking: return
        fullfile = ''
        try:    
            # Genera el nombre de archivo
            path = self.environment.getOutputFolder() + "/" + test.Owner + "/" + test.Monitor 
            if not os.path.exists(path):
                os.makedirs(path)
            month = self.environment.YearMonth
            filename = test.Owner + "-" + test.Monitor + "#" + month + "#" + str(test.Interval) + "-" + str(test.Offset) + "#r1.mon"
            # Calcula la posición que corresponde
            desired_pos = 3 * self.environment.sliceInMonth(test.Interval)
            # Abre el archivo y hace appends hasta llegar a esa posición
            # agregando Codes.R_EMPTY
            fullfile = path + "/" + filename
            f = open(fullfile, 'ab+')
            f.seek(0,2) # move the cursor to the end of the file
            size = f.tell()
            gap = desired_pos - size
            if (gap < 0):
                f.truncate(desired_pos)
            self.FixGap(f, gap)
            # Escribe el valor
            f.write(bytes([result, ms & 0xff, (ms >> 8) & 0xff]))
            f.close()
        except Exception as e:
            self.LogError('Se produjo un error al guardar un resultado. ' + str(e) + ". File: " + fullfile + ".")
            return 
    def FixGap(self, f, gap):
        if gap > 1024:
            kb = bytearray()
            for n in range(1024):
                kb.append(0xFF)
        else:
            kb = None
        while (gap > 0):
            if (gap > 1024):
                f.write(kb)
                gap -= 1024
            else:
                f.write(bytes([0xFF]))
                gap -= 1
         
    def Log(self, line):
        self.logLine("logs", line) 
    
    def Print(self, line):
        if self.environment.PrintToScreen:
            print(line)

    def LogError(self, line):
        self.Print('ERROR: ' + line)
        self.logLine("errors", line) 
    
    def getFilename(self, folder, month):
        return self.environment.getMyFolderLocal() + "/" + folder + "/" + month + ".log"
       
    def logLine(self, folder, line):
        if self.environment.Mocking: return
        
        fullfile  = self.getFilename(folder, self.environment.YearMonth)
        f = open(fullfile, 'a+')
        now = self.environment.now()
        print(str(now) + " - " + line, file=f)
        f.close()
        