# Mod de ejemplo: Clones Locos

MOD_INFO = {
    "nombre": "Clones Locos",
    "version": "1.0",
    "autor": "Fenix",
    "descripcion": "Crea clones automaticamente cada 5 segundos"
}

import time

ultimo_clon = [0]

def inicializar(mascota):
    mascota.modo_clones_locos = True
    ultimo_clon[0] = time.time()
    mascota.mostrar_texto("Modo Clones Locos activado!")

def actualizar(mascota):
    if mascota.modo_clones_locos and time.time() - ultimo_clon[0] > 5:
        mascota.crear_clon_automatico()
        ultimo_clon[0] = time.time()

def finalizar(mascota):
    mascota.modo_clones_locos = False
