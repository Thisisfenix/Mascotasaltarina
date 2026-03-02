# Mod con configuraciones ajustables

MOD_INFO = {
    "nombre": "Velocidad Configurable",
    "version": "1.0",
    "autor": "Fenix",
    "descripcion": "Ajusta la velocidad con un slider"
}

# Configuraciones del mod (se muestran en la interfaz)
MOD_CONFIG = {
    "velocidad": {
        "tipo": "slider",
        "nombre": "Velocidad",
        "min": 1,
        "max": 50,
        "default": 10,
        "descripcion": "Velocidad de movimiento"
    },
    "activar_trail": {
        "tipo": "checkbox",
        "nombre": "Activar Rastro",
        "default": False,
        "descripcion": "Deja un rastro al moverse"
    },
    "color_trail": {
        "tipo": "color",
        "nombre": "Color del Rastro",
        "default": "#ff0000",
        "descripcion": "Color del efecto de rastro"
    }
}

# Variables del mod
config_actual = {}

def inicializar(mascota):
    global config_actual
    # Cargar valores por defecto
    config_actual = {
        "velocidad": MOD_CONFIG["velocidad"]["default"],
        "activar_trail": MOD_CONFIG["activar_trail"]["default"],
        "color_trail": MOD_CONFIG["color_trail"]["default"]
    }
    aplicar_config(mascota)

def aplicar_config(mascota):
    """Aplica la configuración actual"""
    vel = config_actual["velocidad"]
    mascota.vel_x = vel if mascota.vel_x > 0 else -vel
    mascota.vel_y = vel if mascota.vel_y > 0 else -vel
    
    if config_actual["activar_trail"]:
        mascota.trail_enabled = True
        mascota.trail_var.set(True)
        mascota.trail_color = config_actual["color_trail"]
    else:
        mascota.trail_enabled = False
        mascota.trail_var.set(False)

def on_config_change(mascota, key, value):
    """Se llama cuando cambia una configuración"""
    global config_actual
    config_actual[key] = value
    aplicar_config(mascota)
    mascota.mostrar_texto(f"{key}: {value}")
