# Mod: Wallpaper Falso

MOD_INFO = {
    "nombre": "Wallpaper Falso",
    "version": "1.0",
    "autor": "Fenix",
    "descripcion": "Crea un fondo de pantalla falso sobre el real (el usuario no se entera)"
}

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

ventana_fondo = None
fondo_imagen = None

def inicializar(mascota):
    global ventana_fondo, fondo_imagen
    
    # Usar AnkushCat por defecto
    archivo = os.path.join("assets", "AnkushCat.png")
    
    # Si no existe, preguntar
    if not os.path.exists(archivo):
        archivo = filedialog.askopenfilename(
            title="Selecciona imagen de wallpaper falso",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not archivo:
            mascota.mostrar_texto("❌ Cancelado")
            return
    
    # Crear ventana fullscreen detrás de todo
    ventana_fondo = tk.Toplevel(mascota.root)
    ventana_fondo.attributes('-fullscreen', True)
    ventana_fondo.attributes('-topmost', False)
    ventana_fondo.overrideredirect(True)
    
    # Cargar y ajustar imagen
    img = Image.open(archivo)
    img = img.resize((mascota.ancho_pantalla, mascota.alto_pantalla), Image.Resampling.LANCZOS)
    fondo_imagen = ImageTk.PhotoImage(img)
    
    label = tk.Label(ventana_fondo, image=fondo_imagen)
    label.pack()
    
    # Enviar al fondo (detrás de iconos del escritorio)
    ventana_fondo.lower()
    
    mascota.mostrar_texto("🖼️ Wallpaper falso activado!")

def actualizar(mascota):
    pass

def finalizar(mascota):
    global ventana_fondo, fondo_imagen
    
    if ventana_fondo:
        ventana_fondo.destroy()
        ventana_fondo = None
    
    fondo_imagen = None
    mascota.mostrar_texto("🖼️ Wallpaper restaurado")
