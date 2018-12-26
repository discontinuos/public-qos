import sys
import os
from Converter import Converter

class FolderConverter:
    folder = ""
    OutFilename = ""
    FileCount = 0

    def __init__(self, folder):
        self.folder = folder
        self.OutFilename = self.folder + ".csv"

    def Process(self):
        if (os.path.isfile(self.OutFilename)):
            os.remove(self.OutFilename)
        self.FileCount = 0
        files = self.getFiles()
        append = False
        for file in files:    
            converter = Converter(file)
            converter.SaveCSV(self.OutFilename, append)
            append = True
            self.FileCount += 1

    def getFiles(self):
        r = []
        for root, dirs, files in os.walk(self.folder):
            for name in files:
                if name.endswith('.mon'):
                    r.append(os.path.join(root, name))
        return r