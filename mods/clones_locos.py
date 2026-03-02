# Mod de ejemplo: Clones Locos

MOD_INFO = {
    "nombre": "Clones Locos",
    "version": "1.1",
    "autor": "Fenix",
    "descripcion": "Crea clones automaticamente cada 5 segundos (respeta límite de 10)"
}

import time

ultimo_clon = [0]

def inicializar(mascota):
    mascota.modo_clones_locos = True
    ultimo_clon[0] = time.time()
    mascota.mostrar_texto("Modo Clones Locos activado!")

def actualizar(mascota):
    if not hasattr(mascota, 'modo_clones_locos'):
        return
    
    if mascota.modo_clones_locos and time.time() - ultimo_clon[0] > 5:
        # Verificar que no se exceda el límite
        if len(mascota.clones) < mascota.max_clones:
            mascota.crear_clon_automatico()
            ultimo_clon[0] = time.time()
        else:
            # Si llegó al límite, desactivar el mod
            mascota.modo_clones_locos = False
            mascota.mostrar_texto(f"⚠️ Límite de {mascota.max_clones} clones alcanzado")

def finalizar(mascota):
    mascota.modo_clones_locos = False
