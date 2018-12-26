import time 
from Process import Process

print('******* Modo MOCKING *******')
print('- Actualiza (descarga) lista de monitores por url.')
print('- Navega monitores (no registra resultados ni errores).')
print('- Simula actualizar mirrors (arma zips).')
print('****************************')

p = Process()
p.ForceMonitorsUpdate = True
p.ForceMirrorUpdate = True
p.Mocking = True
p.Run()

print ('¡Listo!')