import os

class Functions:
       
    def getFilename(file):
        head, tail = os.path.split(file)
        return tail

    def getFilenameNoExt(file):
        head, tail = os.path.split(file)
        return os.path.splitext(tail)[0]            
