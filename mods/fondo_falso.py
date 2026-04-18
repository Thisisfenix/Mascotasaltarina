# Mod: Wallpaper Falso

MOD_INFO = {
    "nombre": "Wallpaper Falso",
    "version": "1.1",
    "autor": "Fenix",
    "descripcion": "Crea un fondo de pantalla falso sobre el real (detrás de iconos y barra de tareas)"
}

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import ctypes

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
    
    # Crear ventana fullscreen
    ventana_fondo = tk.Toplevel(mascota.root)
    ventana_fondo.attributes('-fullscreen', True)
    ventana_fondo.overrideredirect(True)
    ventana_fondo.attributes('-topmost', False)
    
    # Cargar y ajustar imagen
    img = Image.open(archivo)
    img = img.resize((mascota.ancho_pantalla, mascota.alto_pantalla), Image.Resampling.LANCZOS)
    fondo_imagen = ImageTk.PhotoImage(img)
    
    label = tk.Label(ventana_fondo, image=fondo_imagen)
    label.pack()
    
    # Actualizar para obtener el HWND
    ventana_fondo.update()
    
    # Obtener handle de la ventana
    hwnd = ctypes.windll.user32.GetParent(ventana_fondo.winfo_id())
    
    # Constantes de Windows
    HWND_BOTTOM = 1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
    
    # Enviar ventana al fondo (detrás de todo)
    ctypes.windll.user32.SetWindowPos(
        hwnd, HWND_BOTTOM, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
    )
    
    # Hacer que la ventana sea "desktop wallpaper"
    GWL_EXSTYLE = -20
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TOOLWINDOW = 0x00000080
    
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
    
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
