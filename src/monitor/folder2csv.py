import sys
import os
from FolderConverter import FolderConverter 

file = sys.argv.pop()
if not os.path.isdir(file):
    print ('Directorio no encontrado: ' + file)
else:
    converter = FolderConverter(file)
    converter.Process()

print (str(converter.FileCount) + " archivos procesados.")
