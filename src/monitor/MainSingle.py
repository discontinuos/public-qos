import time 
from Process import Process

while True:
    print ('')
    print ('##################### Iniciando ###########################')
    p = Process()
    p.Run()
    time.sleep(60)

print ('¡Listo!')