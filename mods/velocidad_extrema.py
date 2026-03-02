# Mod de ejemplo: Velocidad Extrema

MOD_INFO = {
    "nombre": "Velocidad Extrema",
    "version": "1.0",
    "autor": "Fenix",
    "descripcion": "Hace que la mascota vaya super rapido"
}

def inicializar(mascota):
    mascota.vel_x = 15 if mascota.vel_x > 0 else -15
    mascota.vel_y = 15 if mascota.vel_y > 0 else -15
    mascota.mostrar_texto("MODO VELOCIDAD EXTREMA!")
