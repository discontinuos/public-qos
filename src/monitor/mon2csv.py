import sys
import os
from Converter import Converter

first = True
for file in sys.argv:
    if not first:
        if not os.path.isfile(file):
            print ('Archivo no encontrado: ' + file)
        else:
            converter = Converter(file)
            converter.Save()
    first = False

print (str(len(sys.argv) - 1) + " archivos procesados.")
