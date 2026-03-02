# SISTEMA DE MODS - ANKUSH CAT

## Estructura de un Mod

Cada mod debe ser un archivo .py en esta carpeta con:

MOD_INFO = {
    "nombre": "Nombre del Mod",
    "version": "1.0",
    "autor": "Tu Nombre",
    "descripcion": "Descripcion breve"
}

def inicializar(mascota):
    # Tu codigo aqui
    mascota.frases.append("Hola desde mod!")
    print("Mod cargado!")

## Funciones Opcionales

def actualizar(mascota):
    # Se ejecuta cada frame
    pass

def on_click(mascota, event):
    # Se ejecuta al hacer clic
    pass

def finalizar(mascota):
    # Se ejecuta al cerrar
    pass
