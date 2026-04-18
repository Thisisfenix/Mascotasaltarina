import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
import random
import os
import getpass
import webbrowser
import json
from pygame import mixer
import psutil
import time
import requests
import sys
import subprocess
import threading
import pystray

# Importar win32gui solo si está disponible, si no, intentar instalarlo
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("pywin32 no está instalado. Intentando instalar...")
    try:
        # Detectar versión de Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        python_cmd = sys.executable
        
        # Intentar instalar pywin32
        subprocess.check_call([python_cmd, "-m", "pip", "install", "pywin32"])
        print("pywin32 instalado correctamente. Reinicia el programa.")
        messagebox.showinfo("Instalación completa", 
                          "pywin32 se instaló correctamente.\nReinicia el programa para usar todas las funciones.")
    except:
        print("No se pudo instalar pywin32 automáticamente.")
        messagebox.showwarning("Módulo faltante", 
                             "pywin32 no está instalado.\nAlgunas funciones estarán deshabilitadas.\n\nPara instalar manualmente:\npip install pywin32")

# Variable global para mantener referencia de imagen principal
_IMAGEN_PRINCIPAL_REF = None

# VERSION DEL PROGRAMA - Se lee desde version.txt
def obtener_version_local():
    try:
        with open('version.txt', 'r') as f:
            return f.read().strip()
    except:
        return "2.0.0"

VERSION_ACTUAL = obtener_version_local()

# Variable global para controlar si ya se reprodujo el video
video_intro_reproducido = False

def verificar_actualizacion_disponible():
    """Verifica si hay actualizacion disponible"""
    try:
        version_local = VERSION_ACTUAL
        # Leer version.txt directamente de GitHub
        version_url = "https://raw.githubusercontent.com/Thisisfenix/Mascotasaltarina/main/HolaGissel/version.txt"
        response = requests.get(version_url, timeout=5)
        
        if response.status_code == 200:
            version_github = response.text.strip()
            
            if version_github != version_local:
                update_info = {
                    'version': version_github,
                    'download_url': 'https://github.com/Thisisfenix/Mascotasaltarina/releases/latest'
                }
                
                # Obtener mensaje del último commit
                try:
                    commit_url = "https://api.github.com/repos/Thisisfenix/Mascotasaltarina/commits/main"
                    commit_response = requests.get(commit_url, timeout=5)
                    if commit_response.status_code == 200:
                        commit_data = commit_response.json()
                        update_info['commit_message'] = commit_data['commit']['message']
                except:
                    pass
                
                return update_info
    except:
        pass
    return None

def mostrar_splash_actualizacion(root_principal):
    """Muestra splash de verificacion de actualizaciones"""
    splash = tk.Toplevel(root_principal)
    splash.title("Ankush Cat")
    splash.geometry("400x250")
    splash.configure(bg='#1e1e2e')
    splash.overrideredirect(True)
    
    x = (splash.winfo_screenwidth() // 2) - 200
    y = (splash.winfo_screenheight() // 2) - 125
    splash.geometry(f"400x250+{x}+{y}")
    
    tk.Label(splash, text="🐱 Ankush Cat", bg='#1e1e2e', fg='#89b4fa',
            font=('Arial', 18, 'bold')).pack(pady=20)
    
    status_label = tk.Label(splash, text="Verificando actualizaciones...", bg='#1e1e2e',
                           fg='#cdd6f4', font=('Arial', 11))
    status_label.pack(pady=10)
    
    commit_label = tk.Label(splash, text="", bg='#1e1e2e', fg='#a5b4fc',
                           font=('Arial', 9), wraplength=360)
    commit_label.pack(pady=5)
    
    tk.Label(splash, text=f"v{VERSION_ACTUAL}", bg='#1e1e2e', fg='#6c7086',
            font=('Arial', 9)).pack(pady=5)
    
    def verificar():
        info = verificar_actualizacion_disponible()
        if info:
            status_label.config(text=f"Nueva version {info['version']} disponible!")
            if 'commit_message' in info:
                commit_msg = info['commit_message'].split('\n')[0][:80]
                commit_label.config(text=f"📝 {commit_msg}")
            splash.after(1000, lambda: preguntar_actualizar(splash, info))
        else:
            status_label.config(text="Iniciando...")
            splash.after(500, splash.destroy)
    
    def preguntar_actualizar(ventana, info):
        ventana.destroy()
        
        version_nueva = info.get('version', '?')
        changelog = info.get('changelog', [])
        
        # Mensaje especial para la v3.0 (migración a C#)
        if version_nueva.startswith('3.'):
            msg = (
                f"⚠️ ACTUALIZACIÓN MAYOR: v{version_nueva}\n\n"
                f"Esta versión es completamente nueva en C# con WPF.\n"
                f"Se instalará junto a esta carpeta.\n\n"
            )
            if changelog:
                msg += "Novedades:\n" + "\n".join(f"  {c}" for c in changelog[:5]) + "\n\n"
            msg += "¿Descargar e instalar la v3.0 ahora?\n(~50-100 MB)"
        else:
            msg = f"Nueva versión {version_nueva} disponible!\n\n¿Actualizar ahora?"
        
        respuesta = messagebox.askyesno(
            f"🚀 Ankush Cat v{version_nueva} disponible!",
            msg
        )
        if respuesta:
            updater_path = os.path.join("assets", "updater", "Updater.exe")
            if os.path.exists(updater_path):
                subprocess.Popen([updater_path])
                sys.exit(0)
            else:
                messagebox.showerror("Error", "No se encontró Updater.exe en assets/updater/")
    
    threading.Thread(target=verificar, daemon=True).start()
    splash.wait_window()

class ImagenFlotante:
    def __init__(self, root_principal):
        global video_intro_reproducido
        # Reproducir video de intro aleatorio solo la primera vez
        if not video_intro_reproducido:
            self.reproducir_video_intro()
            video_intro_reproducido = True
        
        self.root = root_principal
        self.root.title("Control de Imagen Flotante")
        self.root.geometry("450x650")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#0a0e27')
        self.root.deiconify()  # Mostrar la ventana
        
        # Variable para rastrear si hay cambios sin guardar
        self.cambios_sin_guardar = False
        
        # Bandera para evitar cargar imagen durante __init__
        self._inicializando = True
        
        # Lista para mantener TODAS las referencias de imágenes - DEBE IR AL INICIO
        self._image_refs = []
        
        # Establecer icono personalizado - SOLO .ICO
        self.icon_path = None
        try:
            # Intentar con icon.ico en la raíz primero
            icon_path_test = os.path.abspath("icon.ico")
            if os.path.exists(icon_path_test):
                self.root.iconbitmap(icon_path_test)
                self.icon_path = icon_path_test
            else:
                # Intentar en assets
                icon_path_test = os.path.abspath(os.path.join("assets", "icon.ico"))
                if os.path.exists(icon_path_test):
                    self.root.iconbitmap(icon_path_test)
                    self.icon_path = icon_path_test
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        # NO inicializar mixer aquí - moverlo después del label
        
        self.ventana_imagen = tk.Toplevel(self.root)
        self.ventana_imagen.overrideredirect(True)
        self.ventana_imagen.attributes('-topmost', True)
        self.ventana_imagen.attributes('-transparentcolor', 'white')
        self.ventana_imagen.config(bg='white')
        
        self.ventana_texto = None
        self.username = getpass.getuser()
        self.clicks = 0
        self.click_contador = 0
        self.ultimo_click_tiempo = 0
        self.tiempo_inicio = time.time()
        self.distancia_recorrida = 0
        self.historial_clicks = []
        
        # Nuevas variables
        self.trail_enabled = False
        self.trail_color = '#89b4fa'
        self.trail_positions = []
        self.trail_ventanas = []
        self.clones = []
        self.max_clones = 10  # Límite de clones (optimizado para PCs normales)
        self.sonido_path = os.path.join("assets", "sonidito.mp3")
        self.sonido_enabled = False
        self.modo_invisible = False
        self.modo_perseguir = False
        self.zoom_auto = False
        self.zoom_direccion = 1
        self.arrastrando = False
        self.offset_x = 0
        self.offset_y = 0
        self.rebote_elastico = False
        self.rebote_elastico_aumentar = False
        self.escala_x = 1.0
        self.escala_y = 1.0
        self.particulas_mover = False
        self.particulas_lista = []
        self.modo_espejo_h = False
        self.modo_espejo_v = False
        self.modo_orbital = False
        self.arrastre_habilitado = False
        self.angulo_orbital = 0
        self.centro_orbital_x = 400
        self.centro_orbital_y = 400
        self.modo_zigzag = False
        self.zigzag_contador = 0
        self.modo_teletransporte = False
        self.modo_seguir_ventana = False
        self.musica_fondo = False
        self.musica_path = os.path.join("assets", "Music.mp3")
        self.sonidos_eventos = False
        self.modo_screensaver = False
        self.notificaciones = []
        self.clima_modo = False
        self.clima_actual = "soleado"
        self.clima_obtenido = False
        self.rotacion_auto = False
        self.angulo_rotacion = 0
        self.es_gif = False
        self.gif_frames = []
        self.gif_frame_actual = 0
        self.gif_duracion = 100
        self.rotar_al_rebotar = False
        self.sentido_rotacion = 1  # 1 = horario, -1 = antihorario
        self.ultimo_rebote_tiempo = 0
        self.explosion_random = False
        self.modo_bordes = False
        self.borde_actual = 0  # 0=arriba, 1=derecha, 2=abajo, 3=izquierda
        self.modo_drunk = False
        self.sync_clones = False
        self.rebote_loco = False
        self.modo_fantasma = False
        self.modo_espiral = False
        self.espiral_angulo = 0
        self.espiral_radio = 300
        self.modo_ladron = False
        self.ladron_ultimo_robo = 0
        self.modo_ruleta = False
        self.ruleta_ultimo = 0
        self.modo_arcoiris = False
        self.arcoiris_hue = 0
        self.modo_iman = False
        self.modo_paparazzi = False
        self.paparazzi_ultimo = 0
        self.modo_francotirador = False
        self.francotirador_ultimo = 0
        self.modo_graffiti = False
        self.graffiti_activo = False
        self.graffiti_canvas = None
        self.modo_tornado = False
        self.tornado_angulo = 0
        self.tornado_velocidad = 1
        self.modo_camaleon = False
        self.camaleon_imagenes = []
        self.camaleon_indice = 0
        self.camaleon_ultimo = 0
        self.modo_spam = False
        self.spam_ultimo = 0
        self.hambre = 100
        self.felicidad = 100
        self.ultimo_hambre = time.time()
        self.modo_dormir = False
        self.durmiendo = False
        self.ultimo_interaccion = time.time()
        self.banandose = False
        self.ventana_regadera = None
        self.tiempo_bano = 0
        
        # Nuevos modos
        self.modo_doppelganger = False
        self.doppelganger_clon = None
        self.modo_sniper = False
        self.sniper_balas = []
        self.sniper_ultimo_disparo = 0
        self.modo_predictor = False
        self.predictor_historial = []
        self.predictor_prediccion = None
        self.modo_circo = False
        self.circo_ultimo = 0
        self.modo_dados = False
        self.dados_ultimo = 0
        self.modo_repeler = False
        self.modo_bailarin = False
        self.bailarin_musica = None
        self.bailarin_beat = 0
        
        # Nuevas variables para juegos e interacciones
        self.nivel = 1
        self.experiencia = 0
        self.logros = []
        self.inventario = []
        self.estado_animo = "feliz"
        self.modo_huir = False
        self.modo_cazar = False
        self.cazar_inicio = 0
        self.cazar_hp = 100
        self.cazar_activo = False
        
        # Modo Experimental mejorado
        self.exp_nivel_agresion = 0
        self.exp_clones_saltarines = []
        self.exp_invisible_activo = False
        self.exp_grab_activo = False
        self.exp_combo_teclas = []
        self.exp_combo_objetivo = []
        self.exp_ultimo_hit = 0
        self.exp_hardcore = False
        self.exp_ultrahardcore = False
        self.exp_posiciones_raton = []
        self.exp_prediccion_activa = False
        
        # Sistema de Mods
        self.mods_cargados = []
        self.mods_activos = {}
        
        # Sistema de DLCs
        self.dlcs_cargados = []
        self.dlcs_activos = {}
        
        # Sistema de guardado
        self.data_path = os.path.join('assets', 'data', 'save_data.json')
        self.cargar_datos_juego()
        
        self.frases = [
            f"Buenos dias {self.username}",
            "Buenos dias Gissel",
            "Hola soy Ankush Cat Meow",
            "soft gf r34",
            "ehhh error 404",
            "Pls i need this",
            "Laik si take es femboy",
            "Abel 676767",
            "francisco es un pendejo",
            "Pendejo digo Meow",
            "Hola Maau",
            "Where are you Going idk",
            f"Hola {self.username}!",
            "No me toques tanto!",
            "Estoy ocupado",
            "Dejame en paz",
            "Que quieres?"
        ]
        
        self.imagen_path = os.path.join("assets", "AnkushCat.png")
        self.tamano = 100
        self.opacidad = 1.0
        self.rotacion = 0
        
        # Verificar si existe la imagen
        if not os.path.exists(self.imagen_path):
            gif_path = os.path.join("assets", "AnkushCat.gif")
            if os.path.exists(gif_path):
                self.imagen_path = gif_path
            else:
                self.mostrar_error_archivos_faltantes()
                self.root.destroy()
                return
        
        self.ancho_pantalla = self.root.winfo_screenwidth()
        self.alto_pantalla = self.root.winfo_screenheight()
        
        self.x = random.randint(0, self.ancho_pantalla - 100)
        self.y = random.randint(0, self.alto_pantalla - 100)
        self.vel_x = 3
        self.vel_y = 3
        self.activo = True
        self.rebote = True
        self.gravedad = False
        self.vel_gravedad = 0
        self.explotando = False
        self.particulas = []
        
        # CARGAR IMAGEN PIL JUSTO ANTES DE CREAR EL LABEL
        global _IMAGEN_PRINCIPAL_REF
        try:
            img = Image.open(self.imagen_path)
            
            # MANTENER REFERENCIA A LA IMAGEN PIL
            self._pil_image = img
            
            # Verificar si es GIF animado
            if self.imagen_path.lower().endswith('.gif'):
                try:
                    self.es_gif = True
                    self.gif_frames = []
                    
                    img.seek(0)
                    self.gif_duracion = img.info.get('duration', 100)
                    
                    for frame in range(img.n_frames):
                        img.seek(frame)
                        frame_img = img.copy()
                        frame_img = frame_img.resize((self.tamano, self.tamano), Image.Resampling.LANCZOS)
                        # NO crear PhotoImage aquí, solo guardar PIL
                        self.gif_frames.append(frame_img)
                    
                    # Crear PhotoImage del primer frame JUSTO ANTES del label
                    img_resized = self.gif_frames[0]
                    self._pil_image_resized = img_resized
                except Exception as e:
                    self.es_gif = False
            
            if not self.es_gif:
                img_resized = img.resize((self.tamano, self.tamano), Image.Resampling.LANCZOS)
                # MANTENER REFERENCIA A LA IMAGEN REDIMENSIONADA
                self._pil_image_resized = img_resized
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self.root.destroy()
            return
        
        # CREAR PhotoImage JUSTO ANTES de crear el label
        self.imagen = ImageTk.PhotoImage(self._pil_image_resized)
        self._image_refs.append(self.imagen)
        _IMAGEN_PRINCIPAL_REF = self.imagen
        
        # Crear label CON la imagen directamente en el constructor
        self.label = tk.Label(self.ventana_imagen, image=self.imagen, bg='white', cursor='hand2')
        self.label.pack()
        
        # GUARDAR REFERENCIA ADICIONAL EN EL LABEL
        self.label.image = self.imagen
        self.label._imagen_ref = self.imagen
        self.label._pil_ref = self._pil_image
        
        # AHORA inicializar mixer DESPUÉS de crear el label
        mixer.init()
        
        self.label.bind('<Button-1>', self.on_click)
        self.label.bind('<Button-3>', self.menu_contextual)
        self.label.bind('<ButtonPress-1>', self.iniciar_arrastre)
        self.label.bind('<B1-Motion>', self.arrastrar)
        self.label.bind('<ButtonRelease-1>', self.soltar_arrastre)
        
        # Desactivar bandera de inicialización
        self._inicializando = False
        
        self.crear_panel_control()
        self.crear_icono_tray()
        self.verificar_inactividad()
        self.mover()
        # NO llamar mainloop aqui, se llama desde __main__
    
    def on_click(self, event):
        if self.arrastrando:
            return
        tiempo_actual = time.time()
        self.ultimo_interaccion = tiempo_actual
        self.felicidad = min(100, self.felicidad + 2)
        
        # Ejecutar mods
        self.ejecutar_mods_click(event)
        
        self.click_contador += 1
        self.historial_clicks.append(tiempo_actual)
        self.actualizar_contador()
        
        if self.sonido_enabled:
            try:
                sound = mixer.Sound(self.sonido_path)
                sound.play()
            except:
                pass
        
        # Video random con mayor probabilidad
        videos = [
            'https://youtu.be/xpsrlD_UYIU',
            'https://youtu.be/tdWd9rMy-u8'
        ]
        if random.randint(1, 5) == 1:  # Cambiado de 1/8 a 1/5 para mayor probabilidad
            try:
                webbrowser.open(random.choice(videos))
                self.mostrar_texto("🎥 Abriendo video sorpresa!")
            except Exception as e:
                print(f"Error abriendo video: {e}")
        
        if tiempo_actual - self.ultimo_click_tiempo < 0.5:
            self.clicks += 1
        else:
            self.clicks = 1
            
        self.ultimo_click_tiempo = tiempo_actual
        
        if self.clicks >= 15:
            self.advertencia_explosion()
        elif self.clicks >= 10:
            self.mostrar_texto("PARA! Me vas a romper!")
        else:
            frase = random.choice(self.frases)
            self.mostrar_texto(frase)
    
    def advertencia_explosion(self):
        if not self.explotando:
            respuesta = messagebox.askyesno(
                "ADVERTENCIA!",
                "La imagen esta a punto de EXPLOTAR!\n\nQuieres continuar?"
            )
            if respuesta:
                self.explotar()
            else:
                self.clicks = 0
    
    def explotar(self):
        self.explotando = True
        self.activo = False
        
        for i in range(30):
            particula = {
                'x': self.x + self.tamano // 2,
                'y': self.y + self.tamano // 2,
                'vel_x': random.randint(-15, 15),
                'vel_y': random.randint(-15, 15),
                'vida': 50,
                'color': random.choice(['red', 'orange', 'yellow', 'white'])
            }
            self.particulas.append(particula)
        
        self.ventana_imagen.withdraw()
        self.animar_particulas()
    
    def animar_particulas(self):
        if not self.particulas:
            self.reiniciar_despues_explosion()
            return
        
        canvas = tk.Canvas(self.root, width=300, height=300, bg='#1e1e2e', highlightthickness=0)
        canvas.place(x=60, y=200)
        
        particulas_vivas = []
        for p in self.particulas:
            p['x'] += p['vel_x']
            p['y'] += p['vel_y']
            p['vel_y'] += 0.5
            p['vida'] -= 1
            
            if p['vida'] > 0:
                canvas.create_oval(
                    p['x'] - 150, p['y'] - 150,
                    p['x'] - 145, p['y'] - 145,
                    fill=p['color'], outline=''
                )
                particulas_vivas.append(p)
        
        self.particulas = particulas_vivas
        self.root.after(30, lambda: [canvas.destroy(), self.animar_particulas()])
    
    def reiniciar_despues_explosion(self):
        self.explotando = False
        self.activo = True
        self.clicks = 0
        self.particulas = []
        self.x = self.ancho_pantalla // 2
        self.y = self.alto_pantalla // 2
        self.vel_x = 3 if self.vel_x > 0 else -3
        self.vel_y = 3 if self.vel_y > 0 else -3
        self.ventana_imagen.deiconify()
    
    def mostrar_texto(self, texto):
        if self.ventana_texto:
            try:
                self.ventana_texto.destroy()
            except:
                pass
        
        self.ventana_texto = tk.Toplevel(self.root)
        self.ventana_texto.overrideredirect(True)
        self.ventana_texto.attributes('-topmost', True)
        self.ventana_texto.config(bg='black')
        
        main_frame = tk.Frame(self.ventana_texto, bg='black', bd=4, relief='solid')
        main_frame.pack(padx=0, pady=0)
        
        inner_frame = tk.Frame(main_frame, bg='white', bd=2)
        inner_frame.pack(padx=4, pady=4)
        
        content_frame = tk.Frame(inner_frame, bg='white')
        content_frame.pack(padx=10, pady=10)
        
        try:
            img_mini = Image.open(self.imagen_path)
            img_mini = img_mini.resize((60, 60), Image.Resampling.LANCZOS)
            self.img_dialogo = ImageTk.PhotoImage(img_mini)
            self._image_refs.append(self.img_dialogo)  # GUARDAR REFERENCIA
            
            img_label = tk.Label(content_frame, image=self.img_dialogo, bg='white')
            img_label.pack(side='left', padx=5)
        except:
            pass
        
        text_frame = tk.Frame(content_frame, bg='white')
        text_frame.pack(side='left', padx=5)
        
        tk.Label(text_frame, text="*", bg='white', font=('Arial', 14, 'bold'), fg='black').pack(anchor='w')
        
        label = tk.Label(text_frame, text=texto, bg='white', font=('Arial', 11), 
                        fg='black', wraplength=300, justify='left')
        label.pack(anchor='w', pady=2)
        
        self.ventana_texto.update_idletasks()
        ancho_ventana = self.ventana_texto.winfo_width()
        alto_ventana = self.ventana_texto.winfo_height()
        
        texto_x = (self.ancho_pantalla - ancho_ventana) // 2
        texto_y = self.alto_pantalla - alto_ventana - 100
        
        self.ventana_texto.geometry(f"+{texto_x}+{texto_y}")
        self.ventana_texto.lift()
        self.ventana_texto.focus_force()
        
        self.root.after(3000, lambda: self.ventana_texto.destroy() if self.ventana_texto else None)
    
    def cargar_imagen(self):
        try:
            img = Image.open(self.imagen_path)
            
            # Verificar si es GIF animado
            if self.imagen_path.lower().endswith('.gif'):
                try:
                    self.es_gif = True
                    self.gif_frames = []
                    
                    img.seek(0)
                    self.gif_duracion = img.info.get('duration', 100)
                    
                    for frame in range(img.n_frames):
                        img.seek(frame)
                        frame_img = img.copy()
                        if self.modo_espejo_h:
                            frame_img = ImageOps.mirror(frame_img)
                        if self.modo_espejo_v:
                            frame_img = ImageOps.flip(frame_img)
                        ancho = int(self.tamano * self.escala_x)
                        alto = int(self.tamano * self.escala_y)
                        frame_img = frame_img.resize((ancho, alto), Image.Resampling.LANCZOS)
                        if self.rotacion != 0 or self.rotacion_auto:
                            angulo = self.rotacion + (self.angulo_rotacion if self.rotacion_auto else 0)
                            frame_img = frame_img.rotate(angulo, expand=False)
                        photo = ImageTk.PhotoImage(frame_img)
                        self.gif_frames.append(photo)
                        self._image_refs.append(photo)
                    
                    self.imagen = self.gif_frames[0]
                    self._image_refs.append(self.imagen)
                    self.animar_gif()
                except:
                    self.es_gif = False
            
            if not self.es_gif:
                if self.modo_espejo_h:
                    img = ImageOps.mirror(img)
                if self.modo_espejo_v:
                    img = ImageOps.flip(img)
                ancho = int(self.tamano * self.escala_x)
                alto = int(self.tamano * self.escala_y)
                img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
                if self.rotacion != 0 or self.rotacion_auto:
                    angulo = self.rotacion + (self.angulo_rotacion if self.rotacion_auto else 0)
                    img = img.rotate(angulo, expand=False)
                self.imagen = ImageTk.PhotoImage(img)
                self._image_refs.append(self.imagen)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self.imagen = None
    
    def animar_gif(self):
        if self.es_gif and len(self.gif_frames) > 0:
            self.gif_frame_actual = (self.gif_frame_actual + 1) % len(self.gif_frames)
            self.imagen = self.gif_frames[self.gif_frame_actual]
            self.label.config(image=self.imagen)
            self.root.after(self.gif_duracion, self.animar_gif)
    
    def crear_panel_control(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_accent = '#6366f1'
        style_accent2 = '#8b5cf6'
        style_card = '#1e1b4b'
        
        # Header con gradiente simulado
        header = tk.Frame(self.root, bg='#312e81', height=70)
        header.pack(fill='x')
        
        header_inner = tk.Frame(header, bg='#312e81')
        header_inner.pack(expand=True)
        
        tk.Label(header_inner, text="✨", font=("Arial", 24), bg='#312e81', fg='#fbbf24').pack(side='left', padx=5)
        tk.Label(header_inner, text="ANKUSH CAT", font=("Arial", 18, "bold"), bg='#312e81', fg='#e0e7ff').pack(side='left', padx=5)
        tk.Label(header_inner, text="✨", font=("Arial", 24), bg='#312e81', fg='#fbbf24').pack(side='left', padx=5)
        
        # Contenedor principal horizontal
        main_container = tk.Frame(self.root, bg=style_bg)
        main_container.pack(fill='both', expand=True)
        
        # Sidebar izquierdo con navegación vertical
        nav_frame = tk.Frame(main_container, bg='#1e1b4b', width=120)
        nav_frame.pack(side='left', fill='y')
        
        self.pagina_actual = "principal"
        
        nav_buttons = [
            ("Principal", "principal"),
            ("Efectos", "efectos"),
            ("Eventos", "eventos"),
            ("Acciones", "acciones"),
            ("Stats", "stats"),
            ("Juegos", "juegos"),
            ("Mods", "mods"),
            ("DLCs", "dlcs")
        ]
        
        for texto, pagina in nav_buttons:
            btn = tk.Button(nav_frame, text=texto, command=lambda p=pagina: self.cambiar_pagina(p),
                          bg='#6366f1' if pagina == 'principal' else '#1e1b4b', 
                          fg='#ffffff', font=('Arial', 10, 'bold'), 
                          relief='flat', cursor='hand2', width=12, height=2,
                          activebackground='#8b5cf6', activeforeground='#ffffff',
                          bd=0, highlightthickness=0)
            btn.pack(pady=3, padx=5, fill='x')
            setattr(self, f'btn_nav_{pagina}', btn)
        
        # Contenedor derecho para páginas
        shadow_frame = tk.Frame(main_container, bg='#000000')
        shadow_frame.pack(side='right', fill='both', expand=True, padx=3, pady=3)
        
        self.contenedor = tk.Frame(shadow_frame, bg=style_bg)
        self.contenedor.pack(fill='both', expand=True)
        
        self.crear_pagina_principal()
        self.crear_pagina_efectos()
        self.crear_pagina_eventos()
        self.crear_pagina_acciones()
        self.crear_pagina_stats()
        self.crear_pagina_juegos()
        self.crear_pagina_mods()
        self.crear_pagina_dlcs()
        
        self.cambiar_pagina("principal")
        
        # Cargar mods y DLCs al iniciar
        self.cargar_mods()
        self.cargar_dlcs()
        
        # Aplicar datos cargados
        self.aplicar_datos_cargados()
        
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_con_confirmacion)
        
        # Mostrar tutorial si es primera vez
        self.root.after(500, self.mostrar_tutorial)
    
    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        
        # Resetear colores de botones con animación
        for p in ['principal', 'efectos', 'eventos', 'acciones', 'stats', 'juegos', 'mods', 'dlcs']:
            btn = getattr(self, f'btn_nav_{p}')
            if p == pagina:
                btn.config(bg='#6366f1', fg='#ffffff')
            else:
                btn.config(bg='#1e1b4b', fg='#a5b4fc')
        
        # Ocultar todas las páginas
        self.pagina_principal.pack_forget()
        self.pagina_efectos.pack_forget()
        self.pagina_eventos.pack_forget()
        self.pagina_acciones.pack_forget()
        self.pagina_stats.pack_forget()
        self.pagina_juegos.pack_forget()
        self.pagina_mods.pack_forget()
        self.pagina_dlcs.pack_forget()
        
        # Mostrar página seleccionada
        if pagina == "principal":
            self.pagina_principal.pack(fill='both', expand=True)
        elif pagina == "efectos":
            self.pagina_efectos.pack(fill='both', expand=True)
        elif pagina == "eventos":
            self.pagina_eventos.pack(fill='both', expand=True)
        elif pagina == "acciones":
            self.pagina_acciones.pack(fill='both', expand=True)
        elif pagina == "stats":
            self.pagina_stats.pack(fill='both', expand=True)
        elif pagina == "juegos":
            self.pagina_juegos.pack(fill='both', expand=True)
        elif pagina == "mods":
            self.pagina_mods.pack(fill='both', expand=True)
        elif pagina == "dlcs":
            self.pagina_dlcs.pack(fill='both', expand=True)
    
    def crear_pagina_principal(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_principal = tk.Frame(self.contenedor, bg=style_bg)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.pagina_principal, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_principal, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Card de información con diseño moderno
        info_card = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        info_card.pack(pady=10, padx=20, fill='x')
        
        # Borde superior decorativo
        top_border = tk.Frame(info_card, bg='#6366f1', height=3)
        top_border.pack(fill='x')
        
        info_content = tk.Frame(info_card, bg=style_card)
        info_content.pack(pady=15, padx=15)
        
        tk.Label(info_content, text=f"👤 {self.username}", bg=style_card, fg='#a5b4fc', font=('Arial', 10, 'bold')).pack()
        self.contador_label = tk.Label(info_content, text=f"💆 Clicks: {self.click_contador}", bg=style_card, fg='#34d399', font=('Arial', 11, 'bold'))
        self.contador_label.pack(pady=3)
        self.ram_label = tk.Label(info_content, text="💾 RAM: 0%", bg=style_card, fg='#fbbf24', font=('Arial', 10, 'bold'))
        self.ram_label.pack(pady=3)
        self.actualizar_ram()
        
        # Sliders con estilo moderno
        self.crear_slider_en(scrollable_frame, "Velocidad", 1, 20, 3, self.cambiar_velocidad)
        self.crear_slider_en(scrollable_frame, "Tamaño", 30, 400, 100, self.cambiar_tamano)
        self.crear_slider_en(scrollable_frame, "Opacidad", 10, 100, 100, self.cambiar_opacidad)
        self.crear_slider_en(scrollable_frame, "Rotación", 0, 360, 0, self.cambiar_rotacion)
        
        # Checkboxes con mejor espaciado
        check_card = tk.Frame(scrollable_frame, bg=style_card, relief='flat')
        check_card.pack(pady=10, padx=20, fill='x')
        
        check_border = tk.Frame(check_card, bg='#8b5cf6', height=3)
        check_border.pack(fill='x')
        
        check_content = tk.Frame(check_card, bg=style_card)
        check_content.pack(pady=12)
        
        self.rebote_var = tk.BooleanVar(value=True)
        tk.Checkbutton(check_content, text="⚡ Rebote", variable=self.rebote_var, command=self.toggle_rebote, 
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, 
                      font=('Arial', 10, 'bold')).pack(side='left', padx=15)
        
        self.gravedad_var = tk.BooleanVar(value=False)
        tk.Checkbutton(check_content, text="🌍 Gravedad", variable=self.gravedad_var, command=self.toggle_gravedad,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card,
                      font=('Arial', 10, 'bold')).pack(side='left', padx=15)
        
        self.arrastre_var = tk.BooleanVar(value=False)
        tk.Checkbutton(check_content, text="✋ Arrastre", variable=self.arrastre_var, command=self.toggle_arrastre,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card,
                      font=('Arial', 10, 'bold')).pack(side='left', padx=15)
        
        # Botón de acción destacado
        def decir_frase_boton():
            audios = [
                'por-favor-necesito-pito-me-muero.mp3',
                'soy-mencho-wey.mp3',
                'hola-p-nche-p-tita.mp3',
                'homero-gimiendo.mp3'
            ]
            if random.randint(1, 8) == 1:
                try:
                    sound = mixer.Sound(os.path.join("assets", random.choice(audios)))
                    sound.play()
                except:
                    pass
            
            videos = [
                'https://youtu.be/xpsrlD_UYIU',
                'https://youtu.be/tdWd9rMy-u8'
            ]
            if random.randint(1, 8) == 1:
                webbrowser.open(random.choice(videos))
            
            if random.randint(1, 15) == 1:
                self.explotar()
            else:
                self.mostrar_texto(random.choice(self.frases))
        
        btn_frame = tk.Frame(scrollable_frame, bg=style_bg)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="💬 Decir Frase", command=decir_frase_boton, 
                 bg='#8b5cf6', fg='#ffffff', font=('Arial', 11, 'bold'), 
                 relief='flat', cursor='hand2', width=18, height=2,
                 activebackground='#a78bfa', bd=0).pack()
        
        # Estado con indicador visual
        estado_card = tk.Frame(scrollable_frame, bg=style_card, relief='flat')
        estado_card.pack(pady=10, padx=20, fill='x')
        
        estado_border = tk.Frame(estado_card, bg='#34d399', height=3)
        estado_border.pack(fill='x')
        
        self.estado_label = tk.Label(estado_card, text="● Estado: Activo", fg="#34d399", bg=style_card, font=("Arial", 11, "bold"))
        self.estado_label.pack(pady=12)
    
    def crear_pagina_efectos(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_efectos = tk.Frame(self.contenedor, bg=style_bg)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.pagina_efectos, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_efectos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="✨ Efectos Visuales y Sonoros", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Rastro
        rastro_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        rastro_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(rastro_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(rastro_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎨 Efecto de Rastro", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.trail_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar rastro detrás de la imagen", variable=self.trail_var, command=self.toggle_trail,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        tk.Button(content, text="Elegir Color del Rastro", command=self.elegir_color_trail, bg='#8b5cf6', fg='#ffffff', 
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=20).pack(pady=5)
        
        # Partículas
        part_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        part_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(part_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(part_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="✨ Partículas al Mover", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.particulas_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar partículas (estrellas/corazones)", variable=self.particulas_var, command=self.toggle_particulas,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        # Rebote Elástico
        rebote_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        rebote_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(rebote_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(rebote_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="💥 Rebote Elástico", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.rebote_elastico_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar rebote suave y elástico", variable=self.rebote_elastico_var, command=self.toggle_rebote_elastico,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        self.rebote_elastico_aumentar_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Aumentar velocidad", variable=self.rebote_elastico_aumentar_var, command=self.toggle_rebote_elastico_aumentar,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        # Rotación al rebotar
        rotar_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        rotar_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(rotar_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(rotar_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🔄 Rotación al Rebotar", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.rotar_rebote_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Rotar al rebotar en los bordes", variable=self.rotar_rebote_var, command=self.toggle_rotar_rebote,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        sentido_frame = tk.Frame(content, bg=style_card)
        sentido_frame.pack(pady=5)
        tk.Button(sentido_frame, text="⟲ Antihorario", command=lambda: self.cambiar_sentido(-1), bg='#8b5cf6', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        tk.Button(sentido_frame, text="⟳ Horario", command=lambda: self.cambiar_sentido(1), bg='#6366f1', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        
        # Modo Espejo
        espejo_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        espejo_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(espejo_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(espejo_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🪞 Modo Espejo", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        esp_btns = tk.Frame(content, bg=style_card)
        esp_btns.pack(pady=5)
        tk.Button(esp_btns, text="Voltear Horizontal", command=self.toggle_espejo_h, bg='#8b5cf6', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        tk.Button(esp_btns, text="Voltear Vertical", command=self.toggle_espejo_v, bg='#6366f1', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        
        # Sonido
        sonido_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        sonido_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(sonido_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(sonido_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🔊 Sonido al Hacer Clic", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.sonido_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Reproducir sonido al tocar la mascota", variable=self.sonido_var, command=self.toggle_sonido,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        tk.Button(content, text="Cambiar Archivo de Sonido", command=self.cambiar_sonido, bg='#8b5cf6', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=20).pack(pady=5)
        
        # Música de Fondo
        musica_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        musica_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(musica_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(musica_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎵 Música de Fondo", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        
        self.musica_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Reproducir música de fondo", variable=self.musica_var, command=self.toggle_musica,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=3)
        
        tk.Button(content, text="Cambiar Música", command=self.cambiar_musica, bg='#8b5cf6', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=20).pack(pady=5)
        
        # Sonidos por Evento
        eventos_sound_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        eventos_sound_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(eventos_sound_frame, text="🔔 Sonidos por Evento", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        
        self.sonidos_eventos_var = tk.BooleanVar(value=False)
        tk.Checkbutton(eventos_sound_frame, text="Sonidos para rebote, explosión, etc.", variable=self.sonidos_eventos_var, command=self.toggle_sonidos_eventos,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=5)
    
    def crear_pagina_eventos(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_eventos = tk.Frame(self.contenedor, bg=style_bg)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.pagina_eventos, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_eventos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="✨ Modos Especiales", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Modo Invisible
        inv_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        inv_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(inv_frame, text="👻 Modo Invisible", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(inv_frame, text="La imagen desaparece aleatoriamente", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.invisible_var = tk.BooleanVar(value=False)
        tk.Checkbutton(inv_frame, text="Activar modo invisible", variable=self.invisible_var, command=self.toggle_invisible,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Perseguir
        pers_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        pers_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(pers_frame, text="🎯 Modo Perseguir Cursor", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(pers_frame, text="La imagen sigue el movimiento del mouse", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.perseguir_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pers_frame, text="Activar perseguir cursor", variable=self.perseguir_var, command=self.toggle_perseguir,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Zoom Automático
        zoom_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        zoom_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(zoom_frame, text="🔍 Zoom Automático", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(zoom_frame, text="La imagen crece y se encoge automáticamente", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.zoom_var = tk.BooleanVar(value=False)
        tk.Checkbutton(zoom_frame, text="Activar zoom automático", variable=self.zoom_var, command=self.toggle_zoom,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Orbital
        orbital_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        orbital_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(orbital_frame, text="🌌 Modo Orbital", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(orbital_frame, text="La imagen gira alrededor de un punto", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.orbital_var = tk.BooleanVar(value=False)
        tk.Checkbutton(orbital_frame, text="Activar modo orbital", variable=self.orbital_var, command=self.toggle_orbital,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Zigzag
        zigzag_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        zigzag_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(zigzag_frame, text="⚡ Modo Zigzag", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(zigzag_frame, text="Movimiento en zigzag", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.zigzag_var = tk.BooleanVar(value=False)
        tk.Checkbutton(zigzag_frame, text="Activar modo zigzag", variable=self.zigzag_var, command=self.toggle_zigzag,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Teletransporte
        tele_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        tele_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(tele_frame, text="🚀 Modo Teletransporte", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(tele_frame, text="Aparece en lugares aleatorios", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.tele_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tele_frame, text="Activar teletransporte", variable=self.tele_var, command=self.toggle_teletransporte,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Screensaver
        screen_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        screen_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(screen_frame, text="💻 Modo Screensaver", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(screen_frame, text="Múltiples mascotas al estar inactivo", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.screensaver_var = tk.BooleanVar(value=False)
        tk.Checkbutton(screen_frame, text="Activar screensaver", variable=self.screensaver_var, command=self.toggle_screensaver,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Clima
        clima_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        clima_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(clima_frame, text="☁️ Modo Clima", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(clima_frame, text="Comportamiento según el clima", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.clima_var = tk.BooleanVar(value=False)
        tk.Checkbutton(clima_frame, text="Activar modo clima", variable=self.clima_var, command=self.toggle_clima,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Rotación Automática
        rotacion_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        rotacion_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(rotacion_frame, text="🔄 Rotación Automática", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(rotacion_frame, text="La imagen gira continuamente", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.rotacion_auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(rotacion_frame, text="Activar rotación automática", variable=self.rotacion_auto_var, command=self.toggle_rotacion_auto,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Explosión Random
        explosion_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        explosion_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(explosion_frame, text="💣 Explosión Aleatoria", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(explosion_frame, text="La imagen puede explotar en cualquier momento", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.explosion_random_var = tk.BooleanVar(value=False)
        tk.Checkbutton(explosion_frame, text="Activar explosión aleatoria", variable=self.explosion_random_var, command=self.toggle_explosion_random,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Bordes
        bordes_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        bordes_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(bordes_frame, text="🔲 Modo Bordes", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(bordes_frame, text="Recorre el perímetro de la pantalla", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.bordes_var = tk.BooleanVar(value=False)
        tk.Checkbutton(bordes_frame, text="Activar modo bordes", variable=self.bordes_var, command=self.toggle_bordes,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=8)
        
        # Modo Drunk
        drunk_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        drunk_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(drunk_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(drunk_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🍺 Modo Drunk", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Movimiento tambaleante y errático", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.drunk_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo drunk", variable=self.drunk_var, command=self.toggle_drunk,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Rebote Loco
        rebote_loco_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        rebote_loco_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(rebote_loco_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(rebote_loco_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="💨 Modo Rebote Loco", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Cambia dirección aleatoriamente al rebotar", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.rebote_loco_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar rebote loco", variable=self.rebote_loco_var, command=self.toggle_rebote_loco,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Fantasma
        fantasma_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        fantasma_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(fantasma_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(fantasma_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="👻 Modo Fantasma", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Atraviesa las paredes de la pantalla", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.fantasma_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo fantasma", variable=self.fantasma_var, command=self.toggle_fantasma,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Espiral
        espiral_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        espiral_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(espiral_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(espiral_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🌀 Modo Espiral", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Movimiento en espiral hacia el centro", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.espiral_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo espiral", variable=self.espiral_var, command=self.toggle_espiral,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Sincronización Clones
        sync_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        sync_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(sync_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(sync_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🔗 Sincronización Clones", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Los clones se mueven coordinados", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.sync_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar sincronización", variable=self.sync_var, command=self.toggle_sync,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Dormir
        dormir_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        dormir_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(dormir_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(dormir_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="😴 Modo Dormir", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Duerme tras 30s sin interacción", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.dormir_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo dormir", variable=self.dormir_var, command=self.toggle_dormir,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Ladrón de Ventanas
        ladron_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        ladron_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(ladron_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(ladron_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🦹 Modo Ladrón de Ventanas", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Roba y mueve tu ventana activa", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.ladron_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar ladrón de ventanas", variable=self.ladron_var, command=self.toggle_ladron,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Ruleta Rusa
        ruleta_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        ruleta_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(ruleta_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(ruleta_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎲 Modo Ruleta Rusa", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Cada 30s: explotar, 5 clones o +50 XP", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.ruleta_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar ruleta rusa", variable=self.ruleta_var, command=self.toggle_ruleta,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Arcoiris
        arcoiris_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        arcoiris_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(arcoiris_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(arcoiris_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🌈 Modo Arcoiris", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Cambia de color constantemente (RGB)", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.arcoiris_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo arcoiris", variable=self.arcoiris_var, command=self.toggle_arcoiris,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Imán
        iman_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        iman_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(iman_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(iman_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🧲 Modo Imán", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Atrae ventanas hacia la mascota", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.iman_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo imán", variable=self.iman_var, command=self.toggle_iman,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Paparazzi
        paparazzi_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        paparazzi_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(paparazzi_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(paparazzi_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="📸 Modo Paparazzi", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Toma screenshots aleatorios", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.paparazzi_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar paparazzi", variable=self.paparazzi_var, command=self.toggle_paparazzi,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Francotirador
        franco_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        franco_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(franco_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(franco_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎯 Modo Francotirador", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Cierra ventanas aleatorias (¡PELIGROSO!)", bg=style_card, fg='#f38ba8', font=('Arial', 8)).pack()
        
        self.francotirador_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar francotirador", variable=self.francotirador_var, command=self.toggle_francotirador,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Graffiti
        graffiti_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        graffiti_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(graffiti_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(graffiti_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎨 Modo Graffiti", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Dibuja en pantalla con el mouse", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.graffiti_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar graffiti", variable=self.graffiti_var, command=self.toggle_graffiti,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Tornado
        tornado_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        tornado_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(tornado_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(tornado_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🌪️ Modo Tornado", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Gira en círculos arrastrando clones", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.tornado_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar tornado", variable=self.tornado_var, command=self.toggle_tornado,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Camaleón
        camaleon_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        camaleon_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(camaleon_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(camaleon_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎭 Modo Camaleón", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Cambia de imagen cada 5 segundos", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.camaleon_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar camaleón", variable=self.camaleon_var, command=self.toggle_camaleon,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Notificaciones Spam
        spam_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        spam_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(spam_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(spam_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="📱 Modo Notificaciones Spam", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Notificaciones molestas estilo Steam", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.spam_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar spam", variable=self.spam_var, command=self.toggle_spam,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Sistema Mascota
        mascota_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        mascota_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(mascota_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(mascota_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🐾 Sistema Mascota", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Hambre y felicidad", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.hambre_label = tk.Label(content, text="🍖 Hambre: 100%", bg=style_card, fg='#34d399', font=('Arial', 9))
        self.hambre_label.pack(pady=3)
        self.felicidad_label = tk.Label(content, text="😊 Felicidad: 100%", bg=style_card, fg='#fbbf24', font=('Arial', 9))
        self.felicidad_label.pack(pady=3)
        
        btn_mascota_frame = tk.Frame(content, bg=style_card)
        btn_mascota_frame.pack(pady=5)
        tk.Button(btn_mascota_frame, text="🍖 Alimentar", command=self.alimentar, bg='#34d399', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        tk.Button(btn_mascota_frame, text="🚿 Bañar", command=self.iniciar_bano, bg='#60a5fa', fg='#ffffff', font=('Arial', 8, 'bold'), relief='flat').pack(side='left', padx=3)
        
        # Modo Circo
        circo_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        circo_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(circo_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(circo_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎪 Modo Circo", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Trucos aleatorios cada X segundos", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.circo_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo circo", variable=self.circo_var, command=self.toggle_circo,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Dados
        dados_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        dados_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(dados_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(dados_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎲 Modo Dados", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Tira un dado cada 30s con efectos", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.dados_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo dados", variable=self.dados_var, command=self.toggle_dados,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Repeler
        repeler_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        repeler_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(repeler_frame, bg='#6366f1', height=2).pack(fill='x')
        content = tk.Frame(repeler_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🧲 Modo Repeler", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Empuja ventanas lejos (opuesto al imán)", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.repeler_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar modo repeler", variable=self.repeler_var, command=self.toggle_repeler,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        # Modo Bailarín
        bailarin_frame = tk.Frame(scrollable_frame, bg=style_card, relief='flat', bd=0)
        bailarin_frame.pack(pady=8, padx=20, fill='x')
        tk.Frame(bailarin_frame, bg='#8b5cf6', height=2).pack(fill='x')
        content = tk.Frame(bailarin_frame, bg=style_card)
        content.pack(pady=10, padx=15)
        
        tk.Label(content, text="🎵 Modo Bailarín", bg=style_card, fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=3)
        tk.Label(content, text="Baila al ritmo de la música", bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.bailarin_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Activar bailarín", variable=self.bailarin_var, command=self.toggle_bailarin,
                      bg=style_card, fg=style_fg, selectcolor='#312e81', activebackground=style_card, font=('Arial', 9)).pack(pady=5)
        
        self.actualizar_mascota()
    
    def crear_pagina_acciones(self):
        style_bg = '#0a0e27'
        style_card = '#1e1b4b'
        
        self.pagina_acciones = tk.Frame(self.contenedor, bg=style_bg)
        
        tk.Label(self.pagina_acciones, text="⚙️ Acciones y Configuración", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        canvas = tk.Canvas(self.pagina_acciones, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_acciones, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_key(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Up>", _on_key)
        canvas.bind("<Down>", _on_key)
        canvas.focus_set()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        botones = [
            ("🖼️ Cambiar Imagen", self.cambiar_imagen, "#34d399", "Cambia la imagen de la mascota"),
            ("🎨 Cambiar Fondo", self.cambiar_fondo, "#60a5fa", "Cambia el color de fondo"),
            ("⏯️ Pausar/Reanudar", self.pausar, "#8b5cf6", "Pausa o reanuda el movimiento"),
            ("🔄 Reiniciar Posición", self.reiniciar_pos, "#f59e0b", "Vuelve al centro de la pantalla"),
            ("🎲 Posición Aleatoria", self.pos_aleatoria, "#a78bfa", "Teletransporta a posición random"),
            ("👥 Crear Clon", self.crear_clon, "#fbbf24", "Crea una copia de la mascota"),
            ("🗑️ Eliminar Todos los Clones", self.eliminar_clones, "#ef4444", "Elimina todos los clones creados"),
            ("💬 Editor de Frases", self.editor_frases, "#6366f1", "Edita las frases que dice"),
            ("🔊 Cambiar Volumen", self.cambiar_volumen, "#34d399", "Ajusta el volumen de sonidos"),
            ("📸 Captura de Pantalla", self.captura_manual, "#60a5fa", "Toma una captura ahora"),
            ("🎭 Cambiar Opacidad Ventana", self.cambiar_opacidad_ventana, "#8b5cf6", "Ajusta transparencia de la ventana"),
            ("🌈 Cambiar Color Borde", self.cambiar_color_borde, "#a78bfa", "Cambia el color del borde"),
            ("⚡ Resetear Velocidad", self.resetear_velocidad, "#f59e0b", "Vuelve a velocidad normal"),
            ("🎯 Centrar en Pantalla", self.centrar_pantalla, "#fbbf24", "Centra la mascota"),
            ("💾 Guardar Configuración", self.guardar_config, "#8b5cf6", "Guarda todos los ajustes"),
            ("📂 Cargar Configuración", self.cargar_config, "#a78bfa", "Carga ajustes guardados"),
            ("📤 Exportar Estadísticas", self.exportar_stats, "#6366f1", "Exporta stats a archivo"),
            ("🔄 Buscar Actualizaciones", self.buscar_actualizaciones, "#60a5fa", "Verifica si hay updates"),
            ("ℹ️ Acerca de", self.mostrar_acerca_de, "#34d399", "Información del programa"),
            ("❌ Cerrar Programa", self.cerrar_con_confirmacion, "#ef4444", "Cierra la aplicación")
        ]
        
        for texto, comando, color, desc in botones:
            btn_container = tk.Frame(scrollable_frame, bg=style_bg)
            btn_container.pack(pady=8, padx=20, fill='x')
            
            inner_frame = tk.Frame(btn_container, bg=style_card, relief='flat', bd=0)
            inner_frame.pack(fill='x')
            
            top_border = tk.Frame(inner_frame, bg=color, height=3)
            top_border.pack(fill='x')
            
            content = tk.Frame(inner_frame, bg=style_card)
            content.pack(pady=10, padx=15, fill='x')
            
            btn = tk.Button(content, text=texto, command=comando, bg=color, fg='#ffffff',
                          font=('Arial', 11, 'bold'), relief='flat', cursor='hand2',
                          width=25, height=2, bd=0)
            btn.pack()
            
            desc_label = tk.Label(content, text=desc, bg=style_card, fg='#a5b4fc',
                                font=('Arial', 8), wraplength=300)
            desc_label.pack(pady=(5, 0))
            
            def on_enter(e, b=btn, f=inner_frame, c=color):
                b.config(font=('Arial', 13, 'bold'), bg=self.lighten_color(c))
                f.config(relief='raised', bd=3)
            
            def on_leave(e, b=btn, f=inner_frame, c=color):
                b.config(font=('Arial', 11, 'bold'), bg=c)
                f.config(relief='flat', bd=0)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            inner_frame.bind('<Enter>', on_enter)
            inner_frame.bind('<Leave>', on_leave)
    
    def lighten_color(self, hex_color):
        """Aclara un color hexadecimal para el efecto hover"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def crear_pagina_stats(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_stats = tk.Frame(self.contenedor, bg=style_bg)
        
        tk.Label(self.pagina_stats, text="📊 Estadísticas", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        stats_frame = tk.Frame(self.pagina_stats, bg=style_card, relief='flat', bd=0)
        stats_frame.pack(pady=10, padx=20, fill='x')
        tk.Frame(stats_frame, bg='#6366f1', height=3).pack(fill='x')
        content = tk.Frame(stats_frame, bg=style_card)
        content.pack(pady=15, padx=15)
        
        self.tiempo_label = tk.Label(content, text="Tiempo de ejecución: 0s", bg=style_card, fg=style_fg, font=('Arial', 10))
        self.tiempo_label.pack(pady=5)
        
        self.distancia_label = tk.Label(content, text="Distancia recorrida: 0 px", bg=style_card, fg=style_fg, font=('Arial', 10))
        self.distancia_label.pack(pady=5)
        
        self.clicks_total_label = tk.Label(content, text=f"Total de clicks: {self.click_contador}", bg=style_card, fg=style_fg, font=('Arial', 10))
        self.clicks_total_label.pack(pady=5)
        
        tk.Button(content, text="Ver Historial de Clicks", command=self.ver_historial, bg='#8b5cf6', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2').pack(pady=10)
        
        tk.Button(content, text="Reiniciar Estadísticas", command=self.reiniciar_stats, bg='#ef4444', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2').pack(pady=5)
        
        self.actualizar_stats()
    
    def crear_pagina_juegos(self):
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_juegos = tk.Frame(self.contenedor, bg=style_bg)
        
        canvas = tk.Canvas(self.pagina_juegos, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_juegos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="🎮 Juegos e Interacciones", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Sistema de nivel
        nivel_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        nivel_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(nivel_frame, text="⭐ Sistema de Nivel", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        self.nivel_label = tk.Label(nivel_frame, text=f"Nivel: {self.nivel} | XP: {self.experiencia}/100", bg='#313244', fg='#a6e3a1', font=('Arial', 9))
        self.nivel_label.pack(pady=3)
        self.animo_label = tk.Label(nivel_frame, text=f"Estado: {self.estado_animo}", bg='#313244', fg='#f9e2af', font=('Arial', 9))
        self.animo_label.pack(pady=3)
        
        # Piedra papel tijera
        ppt_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        ppt_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(ppt_frame, text="✊✋✌️ Piedra Papel Tijera", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Button(ppt_frame, text="Jugar", command=self.jugar_ppt, bg='#89b4fa', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Atrapar mascota
        atrapar_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        atrapar_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(atrapar_frame, text="🎯 Atrapar la Mascota", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(atrapar_frame, text="Intenta hacer clic en la mascota!", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        tk.Button(atrapar_frame, text="Iniciar Juego", command=self.iniciar_atrapar, bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Modo huir del cursor
        huir_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        huir_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(huir_frame, text="🏃 Huir del Cursor", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(huir_frame, text="La mascota huye cuando te acercas", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        self.huir_var = tk.BooleanVar(value=False)
        tk.Checkbutton(huir_frame, text="Activar modo huir", variable=self.huir_var, command=self.toggle_huir, bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 9)).pack(pady=5)
        
        # Inventario
        inv_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        inv_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(inv_frame, text="🎒 Inventario", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Button(inv_frame, text="Ver Inventario", command=self.ver_inventario, bg='#cba6f7', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Logros
        logros_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        logros_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(logros_frame, text="🏆 Logros", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Button(logros_frame, text="Ver Logros", command=self.ver_logros, bg='#f9e2af', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Adivina la ventana
        adivina_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        adivina_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(adivina_frame, text="🎰 Adivina la Ventana", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(adivina_frame, text="¿Dónde está la mascota?", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        
        self.usar_ventanas_reales_var = tk.BooleanVar(value=False)
        tk.Checkbutton(adivina_frame, text="🔒 Usar mis ventanas reales (castigo: cierra ventana)", variable=self.usar_ventanas_reales_var,
                      bg='#313244', fg=style_fg, selectcolor='#45475a', activebackground='#313244', font=('Arial', 8)).pack(pady=3)
        
        tk.Button(adivina_frame, text="Jugar", command=self.jugar_adivina_ventana, bg='#cba6f7', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Juego de Memoria
        memoria_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        memoria_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(memoria_frame, text="🧠 Juego de Memoria", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(memoria_frame, text="Encuentra las parejas de cartas", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        tk.Button(memoria_frame, text="Jugar", command=self.juego_memoria, bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Test de Reacción
        reaccion_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        reaccion_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(reaccion_frame, text="⚡ Test de Reacción", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(reaccion_frame, text="Mide tu tiempo de reacción", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        tk.Button(reaccion_frame, text="Jugar", command=self.juego_reaccion, bg='#f9e2af', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Esquivar Obstáculos
        esquivar_frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
        esquivar_frame.pack(pady=10, padx=20, fill='x')
        tk.Label(esquivar_frame, text="🎯 Esquiva Obstáculos", bg='#313244', fg=style_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(esquivar_frame, text="Usa las flechas para esquivar", bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack()
        tk.Button(esquivar_frame, text="Jugar", command=self.juego_esquivar, bg='#89dceb', fg='#1e1e2e', font=('Arial', 9, 'bold'), relief='flat', width=15).pack(pady=5)
        
        # Botón experimental
        exp_frame = tk.Frame(scrollable_frame, bg='#f38ba8', relief='solid', bd=3)
        exp_frame.pack(pady=20, padx=20, fill='x')
        tk.Label(exp_frame, text="⚠️ EXPERIMENTAL ⚠️", bg='#f38ba8', fg='#1e1e2e', font=('Arial', 11, 'bold')).pack(pady=5)
        
        # Checkbox Hardcore
        hardcore_frame = tk.Frame(exp_frame, bg='#f38ba8')
        hardcore_frame.pack(pady=5)
        self.hardcore_var = tk.BooleanVar(value=False)
        tk.Checkbutton(hardcore_frame, text="🔥 HARDCORE (Daño x10, Vel x2)", variable=self.hardcore_var, command=self.toggle_hardcore,
                      bg='#f38ba8', fg='#1e1e2e', selectcolor='#1e1e2e', activebackground='#f38ba8', font=('Arial', 9, 'bold')).pack()
        
        # Checkbox UltraHardcore
        ultrahardcore_frame = tk.Frame(exp_frame, bg='#f38ba8')
        ultrahardcore_frame.pack(pady=5)
        self.ultrahardcore_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ultrahardcore_frame, text="💀 ULTRA HARDCORE (Daño x50, Vel x3)", variable=self.ultrahardcore_var, command=self.toggle_ultrahardcore,
                      bg='#f38ba8', fg='#1e1e2e', selectcolor='#1e1e2e', activebackground='#f38ba8', font=('Arial', 9, 'bold')).pack()
        
        tk.Button(exp_frame, text="NO PRESIONAR", command=self.boton_experimental, bg='#1e1e2e', fg='#f38ba8', font=('Arial', 10, 'bold'), relief='raised', width=20, bd=3).pack(pady=10)
    
    def crear_slider_en(self, parent, nombre, desde, hasta, inicial, comando):
        card = tk.Frame(parent, bg='#1e1b4b', relief='flat')
        card.pack(pady=5, padx=20, fill="x")
        
        border = tk.Frame(card, bg='#6366f1', height=2)
        border.pack(fill='x')
        
        content = tk.Frame(card, bg='#1e1b4b')
        content.pack(pady=10, padx=15, fill='x')
        
        tk.Label(content, text=f"{nombre}:", bg='#1e1b4b', fg='#e0e7ff', font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        slider = tk.Scale(content, from_=desde, to=hasta, orient="horizontal", command=comando,
                         bg='#312e81', fg='#e0e7ff', troughcolor='#4c1d95', highlightthickness=0,
                         activebackground='#8b5cf6', relief='flat', font=('Arial', 9, 'bold'),
                         sliderrelief='flat', bd=0)
        slider.set(inicial)
        slider.pack(side="left", fill="x", expand=True, padx=5)
    

    def cambiar_velocidad(self, val):
        velocidad = int(val)
        self.vel_x = velocidad if self.vel_x > 0 else -velocidad
        self.vel_y = velocidad if self.vel_y > 0 else -velocidad
        if not getattr(self, '_inicializando', False):  # Solo marcar cambios si NO estamos inicializando
            self.cambios_sin_guardar = True
    
    def cambiar_tamano(self, val):
        self.tamano = int(val)
        if not getattr(self, '_inicializando', False):  # Solo cargar si NO estamos inicializando
            self.cargar_imagen()
            self.label.config(image=self.imagen)
        self.cambios_sin_guardar = True
    
    def cambiar_opacidad(self, val):
        self.opacidad = int(val) / 100
        if not getattr(self, '_inicializando', False):  # Solo aplicar si NO estamos inicializando
            self.ventana_imagen.attributes('-alpha', self.opacidad)
        self.cambios_sin_guardar = True
    
    def cambiar_rotacion(self, val):
        if not getattr(self, '_inicializando', False):  # Solo procesar si NO estamos inicializando
            if self.es_gif:
                dialog = tk.Toplevel(self.root)
                dialog.title("⚠️ GIF Detectado")
                dialog.geometry("400x200")
                dialog.configure(bg='#1e1e2e')
                dialog.attributes('-topmost', True)
                dialog.resizable(False, False)
                
                tk.Label(dialog, text="⚠️ ADVERTENCIA", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 14, 'bold')).pack(pady=10)
                tk.Label(dialog, text="La rotación con GIFs puede causar\nLAG SEVERO y comportamiento errático.\n\n(El creador es un puto huevón)", 
                        bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10), justify='center').pack(pady=10)
                
                resultado = [None]
                
                def activar():
                    resultado[0] = 'activar'
                    dialog.destroy()
                
                def cambiar():
                    resultado[0] = 'cambiar'
                    dialog.destroy()
                
                def cancelar():
                    resultado[0] = 'cancelar'
                    dialog.destroy()
                
                btn_frame = tk.Frame(dialog, bg='#1e1e2e')
                btn_frame.pack(pady=10)
                tk.Button(btn_frame, text="Activar (Riesgo)", command=activar, bg='#f38ba8', fg='#1e1e2e', 
                         font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
                tk.Button(btn_frame, text="Cambiar Imagen", command=cambiar, bg='#89b4fa', fg='#1e1e2e', 
                         font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
                tk.Button(btn_frame, text="No Hacer Nada", command=cancelar, bg='#313244', fg='#cdd6f4', 
                         font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
                
                dialog.wait_window()
                
                if resultado[0] == 'cambiar':
                    self.cambiar_imagen()
                    return
                elif resultado[0] == 'cancelar' or resultado[0] is None:
                    return
                # Si es 'activar', continúa
            
            self.rotacion = int(val)
            self.cargar_imagen()
            self.label.config(image=self.imagen)
    
    def cambiar_imagen(self):
        archivo = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if archivo:
            self.imagen_path = archivo
            self.es_gif = False
            self.gif_frames = []
            self.cargar_imagen()
            self.label.config(image=self.imagen)
            self.cambios_sin_guardar = True
    
    def cambiar_fondo(self):
        color = colorchooser.askcolor(title="Selecciona color de fondo")
        if color[1]:
            self.ventana_imagen.config(bg=color[1])
            self.ventana_imagen.attributes('-transparentcolor', color[1])
            self.label.config(bg=color[1])
    
    def toggle_rebote(self):
        self.rebote = self.rebote_var.get()
    
    def toggle_gravedad(self):
        self.gravedad = self.gravedad_var.get()
        if self.gravedad:
            self.vel_gravedad = 0
    
    def pausar(self):
        self.activo = not self.activo
        self.estado_label.config(
            text=f"● Estado: {'Activo' if self.activo else 'Pausado'}",
            fg="#a6e3a1" if self.activo else "#f38ba8"
        )
    
    def reiniciar_pos(self):
        self.x = self.ancho_pantalla // 2
        self.y = self.alto_pantalla // 2
        self.vel_x = abs(self.vel_x) * random.choice([-1, 1])
        self.vel_y = abs(self.vel_y) * random.choice([-1, 1])
        self.vel_gravedad = 0
    
    def pos_aleatoria(self):
        self.x = random.randint(0, self.ancho_pantalla - self.tamano)
        self.y = random.randint(0, self.alto_pantalla - self.tamano)
    

    def actualizar_contador(self):
        self.contador_label.config(text=f"Clicks: {self.click_contador}")
    
    def actualizar_ram(self):
        try:
            proceso = psutil.Process(os.getpid())
            ram_mb = proceso.memory_info().rss / (1024**2)
            self.ram_label.config(text=f"RAM: {ram_mb:.1f} MB")
            self.root.after(2000, self.actualizar_ram)
        except:
            pass
    
    def actualizar_stats(self):
        try:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            horas = tiempo_transcurrido // 3600
            minutos = (tiempo_transcurrido % 3600) // 60
            segundos = tiempo_transcurrido % 60
            self.tiempo_label.config(text=f"Tiempo de ejecución: {horas}h {minutos}m {segundos}s")
            self.distancia_label.config(text=f"Distancia recorrida: {int(self.distancia_recorrida)} px")
            self.clicks_total_label.config(text=f"Total de clicks: {self.click_contador}")
            self.root.after(1000, self.actualizar_stats)
        except:
            pass
    
    def reiniciar_stats(self):
        self.tiempo_inicio = time.time()
        self.distancia_recorrida = 0
        self.click_contador = 0
        self.historial_clicks = []
        messagebox.showinfo("Reiniciado", "Estadísticas reiniciadas")
    
    def ver_historial(self):
        if not self.historial_clicks:
            messagebox.showinfo("Historial", "No hay clicks registrados")
            return
        
        hist = tk.Toplevel(self.root)
        hist.title("Historial de Clicks")
        hist.geometry("300x400")
        hist.configure(bg='#1e1e2e')
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                hist.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(hist, text="Últimos Clicks", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=10)
        
        frame = tk.Frame(hist, bg='#1e1e2e')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, bg='#313244', fg='#cdd6f4', font=('Arial', 9))
        for i, t in enumerate(self.historial_clicks[-50:], 1):
            listbox.insert(tk.END, f"Click {i}: {time.strftime('%H:%M:%S', time.localtime(t))}")
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
    
    def toggle_trail(self):
        self.trail_enabled = self.trail_var.get()
        if not self.trail_enabled:
            self.trail_positions = []
            # Limpiar ventanas de estela
            for ventana in self.trail_ventanas:
                try:
                    ventana.destroy()
                except:
                    pass
            self.trail_ventanas = []
    
    def elegir_color_trail(self):
        color = colorchooser.askcolor(title="Color del rastro", initialcolor=self.trail_color)
        if color[1]:
            self.trail_color = color[1]
    
    def toggle_sonido(self):
        self.sonido_enabled = self.sonido_var.get()
    
    def cambiar_sonido(self):
        archivo = filedialog.askopenfilename(title="Selecciona un sonido", filetypes=[("Audio", "*.mp3 *.wav")])
        if archivo:
            self.sonido_path = archivo
    
    def toggle_invisible(self):
        self.modo_invisible = self.invisible_var.get()
    
    def toggle_perseguir(self):
        self.modo_perseguir = self.perseguir_var.get()
    
    def toggle_zoom(self):
        self.zoom_auto = self.zoom_var.get()
    
    def iniciar_arrastre(self, event):
        if self.arrastre_habilitado:
            self.arrastrando = True
            self.offset_x = event.x
            self.offset_y = event.y
    
    def arrastrar(self, event):
        if self.arrastrando and self.arrastre_habilitado:
            self.x = self.ventana_imagen.winfo_x() + event.x - self.offset_x
            self.y = self.ventana_imagen.winfo_y() + event.y - self.offset_y
    
    def soltar_arrastre(self, event):
        if self.arrastre_habilitado:
            self.arrastrando = False
    
    def toggle_arrastre(self):
        self.arrastre_habilitado = self.arrastre_var.get()
    
    def menu_contextual(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg='#313244', fg='#cdd6f4')
        menu.add_command(label="Pausar", command=self.pausar)
        menu.add_command(label="Crear Clon", command=self.crear_clon)
        menu.add_command(label="Posición Aleatoria", command=self.pos_aleatoria)
        menu.add_separator()
        menu.add_command(label="Cerrar", command=self.cerrar)
        menu.post(event.x_root, event.y_root)
    
    def toggle_particulas(self):
        self.particulas_mover = self.particulas_var.get()
    
    def toggle_rebote_elastico(self):
        self.rebote_elastico = self.rebote_elastico_var.get()
    
    def toggle_rebote_elastico_aumentar(self):
        self.rebote_elastico_aumentar = self.rebote_elastico_aumentar_var.get()
    
    def toggle_rotar_rebote(self):
        if self.es_gif:
            dialog = tk.Toplevel(self.root)
            dialog.title("⚠️ GIF Detectado")
            dialog.geometry("400x200")
            dialog.configure(bg='#1e1e2e')
            dialog.attributes('-topmost', True)
            dialog.resizable(False, False)
            
            tk.Label(dialog, text="⚠️ ADVERTENCIA", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 14, 'bold')).pack(pady=10)
            tk.Label(dialog, text="La rotación al rebotar con GIFs\npuede causar LAG SEVERO.\n\n(El creador es un puto huevón)", 
                    bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10), justify='center').pack(pady=10)
            
            resultado = [None]
            
            def activar():
                resultado[0] = 'activar'
                dialog.destroy()
            
            def cambiar():
                resultado[0] = 'cambiar'
                dialog.destroy()
            
            def cancelar():
                resultado[0] = 'cancelar'
                dialog.destroy()
            
            btn_frame = tk.Frame(dialog, bg='#1e1e2e')
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Activar (Riesgo)", command=activar, bg='#f38ba8', fg='#1e1e2e', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Cambiar Imagen", command=cambiar, bg='#89b4fa', fg='#1e1e2e', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame, text="No Hacer Nada", command=cancelar, bg='#313244', fg='#cdd6f4', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            
            dialog.wait_window()
            
            if resultado[0] == 'cambiar':
                self.rotar_rebote_var.set(False)
                self.cambiar_imagen()
                return
            elif resultado[0] == 'cancelar' or resultado[0] is None:
                self.rotar_rebote_var.set(False)
                return
            # Si es 'activar', continúa
        
        self.rotar_al_rebotar = self.rotar_rebote_var.get()
    
    def cambiar_sentido(self, sentido):
        self.sentido_rotacion = sentido
        msg = "Rotación: Horario" if sentido == 1 else "Rotación: Antihorario"
        self.root.after(100, lambda: None)  # Pequeño feedback visual
    
    def toggle_espejo_h(self):
        self.modo_espejo_h = not self.modo_espejo_h
        self.cargar_imagen()
        self.label.config(image=self.imagen)
    
    def toggle_espejo_v(self):
        self.modo_espejo_v = not self.modo_espejo_v
        self.cargar_imagen()
        self.label.config(image=self.imagen)
    
    def toggle_orbital(self):
        self.modo_orbital = self.orbital_var.get()
        if self.modo_orbital:
            self.centro_orbital_x = self.ancho_pantalla // 2
            self.centro_orbital_y = self.alto_pantalla // 2
    
    def toggle_zigzag(self):
        self.modo_zigzag = self.zigzag_var.get()
    
    def toggle_teletransporte(self):
        self.modo_teletransporte = self.tele_var.get()
    
    def toggle_musica(self):
        self.musica_fondo = self.musica_var.get()
        if self.musica_fondo:
            try:
                mixer.music.load(self.musica_path)
                mixer.music.play(-1)
            except:
                pass
        else:
            mixer.music.stop()
    
    def cambiar_musica(self):
        archivo = filedialog.askopenfilename(title="Selecciona música", filetypes=[("Audio", "*.mp3 *.wav")])
        if archivo:
            self.musica_path = archivo
            if self.musica_fondo:
                mixer.music.load(self.musica_path)
                mixer.music.play(-1)
    
    def toggle_sonidos_eventos(self):
        self.sonidos_eventos = self.sonidos_eventos_var.get()
    
    def toggle_screensaver(self):
        self.modo_screensaver = self.screensaver_var.get()
    
    def toggle_clima(self):
        self.clima_modo = self.clima_var.get()
        if self.clima_modo and not self.clima_obtenido:
            self.obtener_clima()
            self.clima_obtenido = True
    
    def toggle_rotacion_auto(self):
        if self.es_gif:
            dialog = tk.Toplevel(self.root)
            dialog.title("⚠️ GIF Detectado")
            dialog.geometry("400x200")
            dialog.configure(bg='#1e1e2e')
            dialog.attributes('-topmost', True)
            dialog.resizable(False, False)
            
            tk.Label(dialog, text="⚠️ ADVERTENCIA", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 14, 'bold')).pack(pady=10)
            tk.Label(dialog, text="La rotación automática con GIFs\npuede causar LAG SEVERO.\n\n(El creador es un puto huevón)", 
                    bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10), justify='center').pack(pady=10)
            
            resultado = [None]
            
            def activar():
                resultado[0] = 'activar'
                dialog.destroy()
            
            def cambiar():
                resultado[0] = 'cambiar'
                dialog.destroy()
            
            def cancelar():
                resultado[0] = 'cancelar'
                dialog.destroy()
            
            btn_frame = tk.Frame(dialog, bg='#1e1e2e')
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Activar (Riesgo)", command=activar, bg='#f38ba8', fg='#1e1e2e', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Cambiar Imagen", command=cambiar, bg='#89b4fa', fg='#1e1e2e', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame, text="No Hacer Nada", command=cancelar, bg='#313244', fg='#cdd6f4', 
                     font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            
            dialog.wait_window()
            
            if resultado[0] == 'cambiar':
                self.rotacion_auto_var.set(False)
                self.cambiar_imagen()
                return
            elif resultado[0] == 'cancelar' or resultado[0] is None:
                self.rotacion_auto_var.set(False)
                return
            # Si es 'activar', continúa
        
        self.rotacion_auto = self.rotacion_auto_var.get()
    
    def obtener_clima(self):
        try:
            response = requests.get("https://wttr.in/?format=j1", timeout=3)
            data = response.json()
            desc = data['current_condition'][0]['weatherDesc'][0]['value'].lower()
            if 'rain' in desc or 'drizzle' in desc:
                self.clima_actual = "lluvioso"
            elif 'cloud' in desc:
                self.clima_actual = "nublado"
            elif 'sun' in desc or 'clear' in desc:
                self.clima_actual = "soleado"
            else:
                self.clima_actual = "normal"
        except:
            self.clima_actual = "normal"
    
    def toggle_explosion_random(self):
        self.explosion_random = self.explosion_random_var.get()
    
    def toggle_bordes(self):
        self.modo_bordes = self.bordes_var.get()
        if self.modo_bordes:
            self.x = 0
            self.y = 0
            self.borde_actual = 0
    
    def toggle_drunk(self):
        self.modo_drunk = self.drunk_var.get()
    
    def toggle_rebote_loco(self):
        self.rebote_loco = self.rebote_loco_var.get()
    
    def toggle_fantasma(self):
        self.modo_fantasma = self.fantasma_var.get()
    
    def toggle_espiral(self):
        self.modo_espiral = self.espiral_var.get()
        if self.modo_espiral:
            self.espiral_angulo = 0
            self.espiral_radio = 300
    
    def toggle_sync(self):
        self.sync_clones = self.sync_var.get()
        if self.sync_clones and len(self.clones) == 0:
            messagebox.showinfo("Aviso", "Necesitas crear clones primero.\nVe a Acciones > Crear Clon")
    
    def toggle_dormir(self):
        self.modo_dormir = self.dormir_var.get()
    
    def toggle_ladron(self):
        self.modo_ladron = self.ladron_var.get()
        if self.modo_ladron:
            self.ladron_ultimo_robo = time.time()
    
    def toggle_ruleta(self):
        self.modo_ruleta = self.ruleta_var.get()
        if self.modo_ruleta:
            self.ruleta_ultimo = time.time()
            self.mostrar_texto("🎲 Ruleta rusa activada!")
    
    def toggle_arcoiris(self):
        self.modo_arcoiris = self.arcoiris_var.get()
    
    def toggle_iman(self):
        self.modo_iman = self.iman_var.get()
    
    def toggle_paparazzi(self):
        self.modo_paparazzi = self.paparazzi_var.get()
        if self.modo_paparazzi:
            self.paparazzi_ultimo = time.time()
            # Crear carpeta screenshots
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
    
    def toggle_francotirador(self):
        if self.francotirador_var.get():
            respuesta = messagebox.askyesno(
                "⚠️ MODO PELIGROSO ⚠️",
                "El Modo Francotirador cerrará ventanas aleatorias cada 20-40 segundos.\n\n¿Estás seguro?"
            )
            if respuesta:
                self.modo_francotirador = True
                self.francotirador_ultimo = time.time()
                self.mostrar_texto("Modo Francotirador activado... 🎯")
            else:
                self.francotirador_var.set(False)
        else:
            self.modo_francotirador = False
    
    def toggle_graffiti(self):
        if self.graffiti_var.get():
            respuesta = messagebox.askyesno(
                "⚠️ MODO GRAFFITI ⚠️",
                "Esto dibujará en tu pantalla siguiendo el mouse.\n\nPresiona ESC para detener.\n\n¿Continuar?"
            )
            if respuesta:
                self.modo_graffiti = True
                self.iniciar_graffiti()
            else:
                self.graffiti_var.set(False)
        else:
            self.modo_graffiti = False
            self.detener_graffiti()
    
    def toggle_tornado(self):
        self.modo_tornado = self.tornado_var.get()
        if self.modo_tornado:
            self.tornado_angulo = 0
            self.tornado_velocidad = 1
            if len(self.clones) == 0:
                messagebox.showinfo("Aviso", "El tornado funciona mejor con clones.\nVe a Acciones > Crear Clon")
    
    def toggle_camaleon(self):
        if self.camaleon_var.get():
            # Crear ventana personalizada para selección de imágenes
            camaleon_win = tk.Toplevel(self.root)
            camaleon_win.title("🎭 Modo Camaleón")
            camaleon_win.geometry("400x500")
            camaleon_win.configure(bg='#1e1e2e')
            camaleon_win.attributes('-topmost', True)
            camaleon_win.resizable(False, False)
            
            tk.Label(camaleon_win, text="🎭 Modo Camaleón", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 14, 'bold')).pack(pady=10)
            tk.Label(camaleon_win, text="Agrega al menos 2 imágenes para el ciclo", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 9)).pack(pady=5)
            
            imagenes_seleccionadas = []
            
            # Frame para lista de imágenes
            lista_frame = tk.Frame(camaleon_win, bg='#313244')
            lista_frame.pack(pady=10, padx=20, fill='both', expand=True)
            
            scrollbar = tk.Scrollbar(lista_frame)
            scrollbar.pack(side='right', fill='y')
            
            listbox = tk.Listbox(lista_frame, yscrollcommand=scrollbar.set, bg='#313244', fg='#cdd6f4', font=('Arial', 9), height=12)
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
            
            def agregar_imagen():
                archivo = filedialog.askopenfilename(
                    title="Selecciona una imagen",
                    filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
                )
                if archivo:
                    imagenes_seleccionadas.append(archivo)
                    nombre = os.path.basename(archivo)
                    listbox.insert(tk.END, f"{len(imagenes_seleccionadas)}. {nombre}")
            
            def eliminar_imagen():
                sel = listbox.curselection()
                if sel:
                    idx = sel[0]
                    imagenes_seleccionadas.pop(idx)
                    listbox.delete(idx)
                    # Reordenar números
                    listbox.delete(0, tk.END)
                    for i, img in enumerate(imagenes_seleccionadas, 1):
                        listbox.insert(tk.END, f"{i}. {os.path.basename(img)}")
            
            def activar_camaleon():
                if len(imagenes_seleccionadas) >= 2:
                    self.camaleon_imagenes = imagenes_seleccionadas
                    self.modo_camaleon = True
                    self.camaleon_indice = 0
                    self.camaleon_ultimo = time.time()
                    self.mostrar_texto(f"Camaleón activado con {len(imagenes_seleccionadas)} imágenes!")
                    camaleon_win.destroy()
                else:
                    messagebox.showwarning("Error", "Necesitas al menos 2 imágenes")
            
            def cancelar():
                self.camaleon_var.set(False)
                camaleon_win.destroy()
            
            # Botones
            btn_frame = tk.Frame(camaleon_win, bg='#1e1e2e')
            btn_frame.pack(pady=10)
            
            tk.Button(btn_frame, text="➕ Agregar Imagen", command=agregar_imagen, bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame, text="➖ Eliminar", command=eliminar_imagen, bg='#f38ba8', fg='#1e1e2e', font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=5)
            
            btn_frame2 = tk.Frame(camaleon_win, bg='#1e1e2e')
            btn_frame2.pack(pady=5)
            
            tk.Button(btn_frame2, text="✔️ Activar", command=activar_camaleon, bg='#89b4fa', fg='#1e1e2e', font=('Arial', 10, 'bold'), width=15).pack(side='left', padx=5)
            tk.Button(btn_frame2, text="❌ Cancelar", command=cancelar, bg='#313244', fg='#cdd6f4', font=('Arial', 10, 'bold'), width=15).pack(side='left', padx=5)
        else:
            self.modo_camaleon = False
    
    def toggle_spam(self):
        self.modo_spam = self.spam_var.get()
        if self.modo_spam:
            self.spam_ultimo = time.time()
    
    def toggle_circo(self):
        self.modo_circo = self.circo_var.get()
        if self.modo_circo:
            self.circo_ultimo = time.time()
            self.mostrar_texto("🎪 Modo circo activado!")
    
    def toggle_dados(self):
        self.modo_dados = self.dados_var.get()
        if self.modo_dados:
            self.dados_ultimo = time.time()
            self.mostrar_texto("🎲 Modo dados activado!")
    
    def toggle_repeler(self):
        self.modo_repeler = self.repeler_var.get()
        if self.modo_repeler:
            self.mostrar_texto("🧲 Modo repeler activado!")
    
    def toggle_bailarin(self):
        if self.bailarin_var.get():
            archivo = filedialog.askopenfilename(
                title="Selecciona música para bailar",
                filetypes=[("Audio", "*.mp3 *.wav")]
            )
            if archivo:
                self.bailarin_musica = archivo
                self.modo_bailarin = True
                self.bailarin_beat = 0
                try:
                    mixer.music.load(self.bailarin_musica)
                    mixer.music.play(-1)
                except:
                    pass
                self.mostrar_texto("🎵 A bailar!")
            else:
                self.bailarin_var.set(False)
        else:
            self.modo_bailarin = False
            mixer.music.stop()
    
    def alimentar(self):
        self.hambre = min(100, self.hambre + 30)
        self.felicidad = min(100, self.felicidad + 10)
        self.ultimo_interaccion = time.time()
        self.mostrar_texto("Ñam ñam! Gracias!")
    
    def iniciar_bano(self):
        if self.banandose:
            return
        self.banandose = True
        self.activo = False
        self.tiempo_bano = time.time()
        
        # Crear ventana de regadera
        self.ventana_regadera = tk.Toplevel(self.root)
        self.ventana_regadera.overrideredirect(True)
        self.ventana_regadera.attributes('-topmost', True)
        self.ventana_regadera.attributes('-transparentcolor', 'white')
        self.ventana_regadera.config(bg='white')
        
        try:
            img_regadera = Image.open(os.path.join("assets", "Regadera.jpg"))
            img_regadera = img_regadera.resize((300, 300), Image.Resampling.LANCZOS)
            self.img_regadera_tk = ImageTk.PhotoImage(img_regadera)
            tk.Label(self.ventana_regadera, image=self.img_regadera_tk, bg='white').pack()
        except:
            pass
        
        # Posicionar regadera en centro
        regadera_x = self.ancho_pantalla // 2 - 150
        regadera_y = self.alto_pantalla // 2 - 150
        self.ventana_regadera.geometry(f"+{regadera_x}+{regadera_y}")
        
        self.animar_bano()
    
    def animar_bano(self):
        if not self.banandose:
            return
        
        # Posición objetivo: centro de la regadera
        regadera_centro_x = self.ancho_pantalla // 2 - self.tamano // 2
        regadera_centro_y = self.alto_pantalla // 2 - self.tamano // 2
        
        dx = regadera_centro_x - self.x
        dy = regadera_centro_y - self.y
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 5:
            self.x += dx / dist * 8
            self.y += dy / dist * 8
            self.ventana_imagen.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.root.after(20, self.animar_bano)
        else:
            # Mascota llegó al centro, reproducir sonido de ducha
            try:
                mixer.music.load(os.path.join("assets", "ducha.mp3"))
                mixer.music.play()
            except:
                pass
            # Esperar 3 segundos
            self.root.after(3000, self.terminar_bano)
    
    def terminar_bano(self):
        # Reproducir sonido final
        try:
            mixer.music.load(os.path.join("assets", "bano-water.mp3"))
            mixer.music.play()
        except:
            pass
        
        # Destruir ventana de regadera
        if self.ventana_regadera:
            self.ventana_regadera.destroy()
            self.ventana_regadera = None
        
        # Aumentar felicidad
        self.felicidad = min(100, self.felicidad + 20)
        self.ultimo_interaccion = time.time()
        
        # Volver a rutina normal
        self.banandose = False
        self.activo = True
        self.mostrar_texto("Ahh! Qué limpio estoy!")
    
    def actualizar_mascota(self):
        try:
            if time.time() - self.ultimo_hambre > 10:
                self.hambre = max(0, self.hambre - 1)
                self.felicidad = max(0, self.felicidad - 0.5)
                self.ultimo_hambre = time.time()
            
            # Actualizar estado de ánimo
            if self.felicidad > 70:
                self.estado_animo = "feliz"
            elif self.felicidad > 40:
                self.estado_animo = "normal"
            elif self.felicidad > 20:
                self.estado_animo = "triste"
            else:
                self.estado_animo = "enojado"
            
            color_hambre = '#a6e3a1' if self.hambre > 50 else '#f9e2af' if self.hambre > 20 else '#f38ba8'
            color_feliz = '#a6e3a1' if self.felicidad > 50 else '#f9e2af' if self.felicidad > 20 else '#f38ba8'
            
            try:
                self.hambre_label.config(text=f"🍖 Hambre: {int(self.hambre)}%", fg=color_hambre)
                self.felicidad_label.config(text=f"😊 Felicidad: {int(self.felicidad)}%", fg=color_feliz)
            except:
                pass
            
            try:
                self.nivel_label.config(text=f"Nivel: {self.nivel} | XP: {self.experiencia}/100")
                self.animo_label.config(text=f"Estado: {self.estado_animo}")
            except:
                pass
            
            if self.modo_dormir and time.time() - self.ultimo_interaccion > 30:
                if not self.durmiendo:
                    self.durmiendo = True
                    self.ventana_imagen.attributes('-alpha', 0.5)
            else:
                if self.durmiendo:
                    self.durmiendo = False
                    self.ventana_imagen.attributes('-alpha', self.opacidad)
            
            self.root.after(1000, self.actualizar_mascota)
        except:
            pass
    
    def verificar_inactividad(self):
        try:
            if self.modo_screensaver:
                try:
                    import ctypes
                    class LASTINPUTINFO(ctypes.Structure):
                        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
                    
                    lii = LASTINPUTINFO()
                    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
                    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                    
                    if millis > 60000 and len(self.clones) < 5:
                        self.crear_clon()
                except:
                    pass
            
            self.root.after(10000, self.verificar_inactividad)
        except:
            pass
    
    def crear_clon(self):
        # Verificar límite de clones
        if len(self.clones) >= self.max_clones:
            messagebox.showwarning("Límite alcanzado", f"No puedes crear más de {self.max_clones} clones")
            return
        
        # Preguntar si quiere usar otra imagen
        respuesta = messagebox.askyesno("Crear Clon", "¿Quieres usar una imagen diferente para el clon?")
        
        imagen_clon = self.imagen
        if respuesta:
            archivo = filedialog.askopenfilename(
                title="Selecciona imagen para el clon",
                filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if archivo:
                try:
                    img = Image.open(archivo)
                    img = img.resize((self.tamano, self.tamano), Image.Resampling.LANCZOS)
                    imagen_clon = ImageTk.PhotoImage(img)
                    self._image_refs.append(imagen_clon)  # GUARDAR REFERENCIA
                except:
                    messagebox.showerror("Error", "No se pudo cargar la imagen")
                    return
            else:
                return
        
        clon = tk.Toplevel(self.root)
        clon.overrideredirect(True)
        clon.attributes('-topmost', True)
        clon.attributes('-transparentcolor', 'white')
        clon.config(bg='white')
        
        label_clon = tk.Label(clon, image=imagen_clon, bg='white')
        label_clon.pack()
        
        x_clon = random.randint(0, self.ancho_pantalla - self.tamano)
        y_clon = random.randint(0, self.alto_pantalla - self.tamano)
        clon.geometry(f"+{x_clon}+{y_clon}")
        
        self.clones.append({'ventana': clon, 'x': x_clon, 'y': y_clon, 'vel_x': random.randint(-5, 5), 'vel_y': random.randint(-5, 5), 'imagen': imagen_clon})
        
        # Mostrar aviso si hay modos que requieren clones
        if len(self.clones) == 1:
            self.verificar_modos_con_clones()
    
    def verificar_modos_con_clones(self):
        """Verifica y muestra qué modos activos requieren clones"""
        modos_con_clones = []
        
        if self.sync_clones:
            modos_con_clones.append("• Sincronización de Clones")
        if self.modo_tornado:
            modos_con_clones.append("• Modo Tornado")
        if self.modo_screensaver:
            modos_con_clones.append("• Modo Screensaver (crea clones automáticamente)")
        
        if modos_con_clones:
            mensaje = "Modos activos que usan clones:\n\n" + "\n".join(modos_con_clones)
            messagebox.showinfo("Modos con Clones", mensaje)
    
    def eliminar_clones(self):
        """Elimina todos los clones creados"""
        for clon in self.clones:
            try:
                clon['ventana'].destroy()
            except:
                pass
        self.clones = []
        messagebox.showinfo("Clones eliminados", "Todos los clones han sido eliminados")
    
    def cambiar_volumen(self):
        """Cambia el volumen de los sonidos"""
        volumen = simpledialog.askfloat("Volumen", "Ingresa el volumen (0.0 a 1.0):", minvalue=0.0, maxvalue=1.0)
        if volumen is not None:
            mixer.music.set_volume(volumen)
            messagebox.showinfo("Volumen", f"Volumen ajustado a {int(volumen*100)}%")
    
    def captura_manual(self):
        """Toma una captura de pantalla manualmente"""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/screenshot_{timestamp}.png"
            screenshot.save(filename)
            messagebox.showinfo("Captura", f"Screenshot guardado en:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo tomar la captura: {e}")
    
    def cambiar_opacidad_ventana(self):
        """Cambia la opacidad de la ventana de control"""
        opacidad = simpledialog.askfloat("Opacidad Ventana", "Ingresa la opacidad (0.1 a 1.0):", minvalue=0.1, maxvalue=1.0)
        if opacidad is not None:
            self.root.attributes('-alpha', opacidad)
    
    def cambiar_color_borde(self):
        """Cambia el color del borde de la ventana"""
        color = colorchooser.askcolor(title="Color del borde")
        if color[1]:
            messagebox.showinfo("Color", f"Color seleccionado: {color[1]}")
    
    def resetear_velocidad(self):
        """Resetea la velocidad a valores normales"""
        self.vel_x = 3 if self.vel_x > 0 else -3
        self.vel_y = 3 if self.vel_y > 0 else -3
        messagebox.showinfo("Velocidad", "Velocidad reseteada a 3")
    
    def centrar_pantalla(self):
        """Centra la mascota en la pantalla"""
        self.x = self.ancho_pantalla // 2 - self.tamano // 2
        self.y = self.alto_pantalla // 2 - self.tamano // 2
    
    def exportar_stats(self):
        """Exporta las estadísticas a un archivo"""
        try:
            tiempo_total = int(time.time() - self.tiempo_inicio)
            stats = {
                'tiempo_ejecucion': tiempo_total,
                'distancia_recorrida': int(self.distancia_recorrida),
                'clicks_totales': self.click_contador,
                'nivel': self.nivel,
                'experiencia': self.experiencia,
                'logros': self.logros,
                'inventario': self.inventario
            }
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"stats_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Exportado", f"Estadísticas exportadas a:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
    
    def buscar_actualizaciones(self):
        """Busca actualizaciones manualmente"""
        info = verificar_actualizacion_disponible()
        if info:
            respuesta = messagebox.askyesno(
                "Actualización disponible",
                f"Nueva versión {info['version']} disponible!\n\n¿Actualizar ahora?"
            )
            if respuesta:
                updater_path = os.path.join("assets", "updater", "Updater.exe")
                if os.path.exists(updater_path):
                    subprocess.Popen([updater_path])
                    sys.exit(0)
                else:
                    messagebox.showerror("Error", "No se encontró Updater.exe en assets/updater/")
        else:
            messagebox.showinfo("Actualizado", f"Ya tienes la última versión ({VERSION_ACTUAL})")
    
    def crear_pagina_mods(self):
        """Crea la página de mods"""
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_mods = tk.Frame(self.contenedor, bg=style_bg)
        
        tk.Label(self.pagina_mods, text="🔧 Sistema de Mods", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        info_frame = tk.Frame(self.pagina_mods, bg=style_card, relief='flat', bd=0)
        info_frame.pack(pady=10, padx=20, fill='x')
        tk.Frame(info_frame, bg='#6366f1', height=3).pack(fill='x')
        content = tk.Frame(info_frame, bg=style_card)
        content.pack(pady=15, padx=15)
        
        tk.Label(content, text="Los mods se cargan desde la carpeta 'mods/'", bg=style_card, fg=style_fg, font=('Arial', 10)).pack(pady=5)
        tk.Label(content, text=f"Mods cargados: {len(self.mods_cargados)}", bg=style_card, fg='#a6e3a1', font=('Arial', 10, 'bold')).pack(pady=5)
        
        btn_frame = tk.Frame(content, bg=style_card)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 Recargar", command=self.cargar_mods, bg='#8b5cf6', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=15).pack(side='left', padx=5)
        tk.Button(btn_frame, text="📂 Abrir Carpeta", command=self.abrir_carpeta_mods, bg='#6366f1', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=15).pack(side='left', padx=5)
        
        # Canvas con scrollbar para lista de mods
        canvas = tk.Canvas(self.pagina_mods, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_mods, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        if not self.mods_cargados:
            tk.Label(scrollable_frame, text="No hay mods cargados", bg=style_bg, fg='#a6a6a6', font=('Arial', 10)).pack(pady=30)
        else:
            for mod in self.mods_cargados:
                mod_card = tk.Frame(scrollable_frame, bg=style_card, relief='solid', bd=1)
                mod_card.pack(pady=8, padx=10, fill='x')
                
                # Header con checkbox
                header = tk.Frame(mod_card, bg='#313244')
                header.pack(fill='x')
                
                # Checkbox para activar/desactivar
                mod_var = tk.BooleanVar(value=mod.get('activo', False))  # Desactivado por defecto
                mod['var'] = mod_var
                
                def toggle_mod(m=mod, v=mod_var):
                    m['activo'] = v.get()
                    if v.get():
                        if hasattr(m['module'], 'inicializar'):
                            try:
                                m['module'].inicializar(self)
                            except Exception as e:
                                import traceback
                                error_msg = f"Error al activar {m.get('nombre', 'mod')}:\n{traceback.format_exc()}"
                                messagebox.showerror("Error en mod", error_msg)
                                v.set(False)
                                m['activo'] = False
                    else:
                        if hasattr(m['module'], 'finalizar'):
                            try:
                                m['module'].finalizar(self)
                            except Exception as e:
                                import traceback
                                error_msg = f"Error al desactivar {m.get('nombre', 'mod')}:\n{traceback.format_exc()}"
                                messagebox.showerror("Error en mod", error_msg)
                    
                    # Guardar automáticamente
                    self.guardar_datos_juego()
                
                tk.Checkbutton(header, text=f"📦 {mod.get('nombre', 'Sin nombre')}", variable=mod_var, 
                              command=toggle_mod, bg='#313244', fg='#89b4fa', selectcolor='#1e1b4b',
                              activebackground='#313244', font=('Arial', 10, 'bold')).pack(side='left', padx=10, pady=8)
                
                # Botón de configuración si el mod tiene MOD_CONFIG
                if hasattr(mod['module'], 'MOD_CONFIG'):
                    def abrir_config(m=mod):
                        self.mostrar_config_mod(m)
                    tk.Button(header, text="⚙️", command=abrir_config,
                             bg='#6366f1', fg='#ffffff', font=('Arial', 8, 'bold'), 
                             relief='flat', cursor='hand2', width=3).pack(side='right', padx=10)
                
                # Info del mod
                info = tk.Frame(mod_card, bg=style_card)
                info.pack(fill='x', padx=10, pady=5)
                
                tk.Label(info, text=f"Versión: {mod.get('version', '?')} | Autor: {mod.get('autor', '?')}", 
                        bg=style_card, fg='#a6a6a6', font=('Arial', 8)).pack(anchor='w')
                tk.Label(info, text=mod.get('descripcion', 'Sin descripción'), 
                        bg=style_card, fg='#cdd6f4', font=('Arial', 9), wraplength=340, justify='left').pack(anchor='w', pady=3)
    
    def cargar_mods(self):
        """Carga los mods desde la carpeta mods/"""
        # Mostrar ventana de carga
        loading = tk.Toplevel(self.root)
        loading.title("Cargando")
        loading.geometry("200x100")
        loading.configure(bg='#1e1e2e')
        loading.attributes('-topmost', True)
        loading.resizable(False, False)
        loading.overrideredirect(True)
        
        x = (self.ancho_pantalla - 200) // 2
        y = (self.alto_pantalla - 100) // 2
        loading.geometry(f"200x100+{x}+{y}")
        
        tk.Label(loading, text="⏳ Cargando mods...", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=20)
        
        # Canvas para el círculo giratorio
        canvas = tk.Canvas(loading, width=40, height=40, bg='#1e1e2e', highlightthickness=0)
        canvas.pack()
        
        angulo = [0]
        def animar_carga():
            canvas.delete('all')
            canvas.create_arc(5, 5, 35, 35, start=angulo[0], extent=90, outline='#6366f1', width=3, style='arc')
            angulo[0] = (angulo[0] + 10) % 360
            if loading.winfo_exists():
                loading.after(50, animar_carga)
        
        animar_carga()
        loading.update()
        
        self.mods_cargados = []
        mods_dir = 'mods'
        errores_mods = []
        
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
            loading.destroy()
            messagebox.showinfo("Carpeta creada", "Se creó la carpeta 'mods/'. Coloca tus archivos .py ahí.")
            return
        
        import importlib.util
        import traceback
        
        for filename in os.listdir(mods_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    filepath = os.path.join(mods_dir, filename)
                    spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    if hasattr(mod, 'MOD_INFO'):
                        mod_info = mod.MOD_INFO.copy()
                        mod_info['module'] = mod
                        mod_info['activo'] = False  # Desactivado por defecto
                        self.mods_cargados.append(mod_info)
                    else:
                        errores_mods.append(f"{filename}: Falta MOD_INFO")
                except Exception as e:
                    tb = traceback.format_exc()
                    error_msg = f"{filename}:\n{tb}"
                    errores_mods.append(error_msg)
        
        loading.destroy()
        
        # Mostrar resultados
        if self.mods_cargados and not errores_mods:
            messagebox.showinfo("Mods cargados", f"Se cargaron {len(self.mods_cargados)} mods exitosamente")
        elif self.mods_cargados and errores_mods:
            msg = f"Se cargaron {len(self.mods_cargados)} mods, pero hubo {len(errores_mods)} errores:\n\n"
            msg += "\n\n".join(errores_mods[:3])  # Mostrar solo primeros 3 errores
            if len(errores_mods) > 3:
                msg += f"\n\n... y {len(errores_mods) - 3} errores más"
            messagebox.showwarning("Mods con errores", msg)
        elif errores_mods:
            msg = f"No se pudo cargar ningún mod. Errores:\n\n"
            msg += "\n\n".join(errores_mods[:3])
            if len(errores_mods) > 3:
                msg += f"\n\n... y {len(errores_mods) - 3} errores más"
            messagebox.showerror("Error cargando mods", msg)
        
        # Refrescar la página de mods
        self.refrescar_pagina_mods()
    
    def abrir_carpeta_mods(self):
        """Abre la carpeta de mods en el explorador"""
        mods_dir = 'mods'
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
        os.startfile(mods_dir)
    
    def crear_pagina_dlcs(self):
        """Crea la página de DLCs"""
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_dlcs = tk.Frame(self.contenedor, bg=style_bg)
        
        tk.Label(self.pagina_dlcs, text="🎮 DLCs - Contenido Descargable", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        info_frame = tk.Frame(self.pagina_dlcs, bg=style_card, relief='flat', bd=0)
        info_frame.pack(pady=10, padx=20, fill='x')
        tk.Frame(info_frame, bg='#6366f1', height=3).pack(fill='x')
        content = tk.Frame(info_frame, bg=style_card)
        content.pack(pady=15, padx=15)
        
        tk.Label(content, text="Los DLCs se cargan desde la carpeta 'dlc/'", bg=style_card, fg=style_fg, font=('Arial', 10)).pack(pady=5)
        tk.Label(content, text=f"DLCs cargados: {len(self.dlcs_cargados)}", bg=style_card, fg='#a6e3a1', font=('Arial', 10, 'bold')).pack(pady=5)
        
        btn_frame = tk.Frame(content, bg=style_card)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 Recargar", command=self.cargar_dlcs, bg='#8b5cf6', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=15).pack(side='left', padx=5)
        tk.Button(btn_frame, text="📂 Abrir Carpeta", command=self.abrir_carpeta_dlcs, bg='#6366f1', fg='#ffffff',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2', width=15).pack(side='left', padx=5)
        
        # Canvas con scrollbar para lista de DLCs
        canvas = tk.Canvas(self.pagina_dlcs, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_dlcs, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        if not self.dlcs_cargados:
            tk.Label(scrollable_frame, text="No hay DLCs cargados", bg=style_bg, fg='#a6a6a6', font=('Arial', 10)).pack(pady=30)
        else:
            for dlc in self.dlcs_cargados:
                dlc_card = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=2)
                dlc_card.pack(pady=10, padx=10, fill='x')
                
                # Header con gradiente
                header = tk.Frame(dlc_card, bg='#6366f1')
                header.pack(fill='x')
                tk.Label(header, text=f"🎮 {dlc.get('nombre', 'DLC')}", bg='#6366f1', fg='#ffffff', font=('Arial', 11, 'bold')).pack(pady=8)
                
                # Info del DLC
                info = tk.Frame(dlc_card, bg='#313244')
                info.pack(fill='x', padx=15, pady=10)
                
                tk.Label(info, text=f"Versión: {dlc.get('version', '?')} | Autor: {dlc.get('autor', '?')}", 
                        bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack(anchor='w', pady=3)
                tk.Label(info, text=dlc.get('descripcion', 'Sin descripción'), 
                        bg='#313244', fg='#cdd6f4', font=('Arial', 9), wraplength=340, justify='left').pack(anchor='w', pady=5)
                
                # Separador
                tk.Frame(dlc_card, bg='#45475a', height=1).pack(fill='x', padx=10)
                
                # Botón para abrir interfaz del DLC
                btn_frame = tk.Frame(dlc_card, bg='#313244')
                btn_frame.pack(fill='x', padx=15, pady=15)
                
                def abrir_dlc(d=dlc):
                    if hasattr(d['module'], 'obtener_interfaz'):
                        d['module'].obtener_interfaz(self)
                    else:
                        messagebox.showwarning("DLC Incompatible", 
                                             f"El DLC {d.get('nombre', 'desconocido')} no tiene interfaz compatible")
                
                tk.Button(btn_frame, text="🚀 Abrir DLC", command=abrir_dlc,
                         bg='#6366f1', fg='#ffffff', font=('Arial', 12, 'bold'), 
                         relief='flat', cursor='hand2', width=25, height=2).pack()
    
    def cargar_dlcs(self):
        """Carga los DLCs desde la carpeta dlc/"""
        self.dlcs_cargados = []
        dlc_dir = 'dlc'
        
        if not os.path.exists(dlc_dir):
            os.makedirs(dlc_dir)
            messagebox.showinfo("Carpeta creada", "Se creó la carpeta 'dlc/'. Coloca tus archivos .py ahí.")
            self.refrescar_pagina_dlcs()
            return
        
        import importlib.util
        import traceback
        
        for filename in os.listdir(dlc_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    filepath = os.path.join(dlc_dir, filename)
                    spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
                    dlc = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dlc)
                    
                    if hasattr(dlc, 'DLC_INFO'):
                        dlc_info = dlc.DLC_INFO.copy()
                        dlc_info['module'] = dlc
                        self.dlcs_cargados.append(dlc_info)
                        
                        if hasattr(dlc, 'inicializar'):
                            try:
                                dlc.inicializar(self)
                            except Exception as e:
                                print(f"Error inicializando DLC {filename}: {e}")
                except Exception as e:
                    tb = traceback.format_exc()
                    print(f"Error cargando DLC {filename}:\n{tb}")
        
        if self.dlcs_cargados:
            messagebox.showinfo("DLCs cargados", f"Se cargaron {len(self.dlcs_cargados)} DLC(s) exitosamente")
        
        self.refrescar_pagina_dlcs()
    
    def abrir_carpeta_dlcs(self):
        """Abre la carpeta de DLCs en el explorador"""
        dlc_dir = 'dlc'
        if not os.path.exists(dlc_dir):
            os.makedirs(dlc_dir)
        os.startfile(dlc_dir)
    
    def refrescar_pagina_dlcs(self):
        """Refresca la página de DLCs para mostrar los cambios"""
        if self.pagina_actual == "dlcs" and hasattr(self, 'pagina_dlcs'):
            self.pagina_dlcs.pack_forget()
        
        if hasattr(self, 'pagina_dlcs'):
            self.pagina_dlcs.destroy()
        
        self.crear_pagina_dlcs()
        
        if self.pagina_actual == "dlcs":
            self.pagina_dlcs.pack(fill='both', expand=True)
    
    def refrescar_pagina_mods(self):
        """Refresca la página de mods para mostrar los cambios"""
        # Si estamos en la página de mods, ocultarla primero
        if self.pagina_actual == "mods" and hasattr(self, 'pagina_mods'):
            self.pagina_mods.pack_forget()
        
        # Destruir la página actual y recrearla
        if hasattr(self, 'pagina_mods'):
            self.pagina_mods.destroy()
        
        self.crear_pagina_mods()
        
        # Si estamos en la página de mods, mostrarla
        if self.pagina_actual == "mods":
            self.pagina_mods.pack(fill='both', expand=True)
    
    def mostrar_config_mod(self, mod):
        """Muestra ventana de configuración para un mod"""
        if not hasattr(mod['module'], 'MOD_CONFIG'):
            messagebox.showinfo("Sin configuración", f"{mod.get('nombre', 'Este mod')} no tiene opciones configurables")
            return
        
        config_win = tk.Toplevel(self.root)
        config_win.title(f"⚙️ Configurar {mod.get('nombre', 'Mod')}")
        config_win.geometry("450x500")
        config_win.configure(bg='#1e1e2e')
        config_win.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                config_win.iconbitmap(self.icon_path)
        except:
            pass
        
        # Header
        header = tk.Frame(config_win, bg='#312e81', height=60)
        header.pack(fill='x')
        tk.Label(header, text=f"⚙️ {mod.get('nombre', 'Mod')}", 
                 bg='#312e81', fg='#e0e7ff', font=('Arial', 14, 'bold')).pack(pady=15)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(config_win, bg='#1e1e2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(config_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=420)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        MOD_CONFIG = mod['module'].MOD_CONFIG
        
        # Crear controles para cada configuración
        for key, config in MOD_CONFIG.items():
            card = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
            card.pack(pady=8, padx=10, fill='x')
            
            # Header del control
            header_control = tk.Frame(card, bg='#45475a')
            header_control.pack(fill='x')
            tk.Label(header_control, text=config.get('nombre', key), 
                    bg='#45475a', fg='#cdd6f4', font=('Arial', 10, 'bold')).pack(side='left', padx=10, pady=5)
            
            # Contenido
            content = tk.Frame(card, bg='#313244')
            content.pack(fill='x', padx=10, pady=10)
            
            # Descripción
            if 'descripcion' in config:
                tk.Label(content, text=config['descripcion'], 
                        bg='#313244', fg='#a6a6a6', font=('Arial', 8)).pack(anchor='w', pady=(0, 5))
            
            tipo = config.get('tipo', 'text')
            
            if tipo == 'slider':
                # Slider
                frame_slider = tk.Frame(content, bg='#313244')
                frame_slider.pack(fill='x')
                
                valor_label = tk.Label(frame_slider, text=str(config.get('default', 0)), 
                                      bg='#313244', fg='#89b4fa', font=('Arial', 9, 'bold'))
                valor_label.pack(side='right', padx=5)
                
                def on_slider_change(val, k=key, lbl=valor_label):
                    lbl.config(text=str(int(float(val))))
                    if hasattr(mod['module'], 'on_config_change'):
                        mod['module'].on_config_change(self, k, int(float(val)))
                
                slider = tk.Scale(frame_slider, from_=config.get('min', 0), to=config.get('max', 100),
                                orient="horizontal", command=on_slider_change,
                                bg='#45475a', fg='#cdd6f4', troughcolor='#1e1e2e',
                                highlightthickness=0, activebackground='#6366f1',
                                relief='flat', font=('Arial', 8), sliderrelief='flat', bd=0)
                slider.set(config.get('default', 0))
                slider.pack(side='left', fill='x', expand=True)
                
            elif tipo == 'checkbox':
                # Checkbox
                var = tk.BooleanVar(value=config.get('default', False))
                
                def on_check_change(k=key, v=var):
                    if hasattr(mod['module'], 'on_config_change'):
                        mod['module'].on_config_change(self, k, v.get())
                
                check = tk.Checkbutton(content, text="Activar", variable=var, command=on_check_change,
                                      bg='#313244', fg='#cdd6f4', selectcolor='#1e1e2e',
                                      activebackground='#313244', font=('Arial', 9))
                check.pack(anchor='w')
                
            elif tipo == 'color':
                # Selector de color
                color_actual = [config.get('default', '#ffffff')]
                
                frame_color = tk.Frame(content, bg='#313244')
                frame_color.pack(fill='x')
                
                color_preview = tk.Label(frame_color, text="   ", bg=color_actual[0], 
                                        relief='solid', bd=2, width=4)
                color_preview.pack(side='left', padx=5)
                
                def elegir_color(k=key, prev=color_preview, col=color_actual):
                    color = colorchooser.askcolor(title="Elegir color", initialcolor=col[0])
                    if color[1]:
                        col[0] = color[1]
                        prev.config(bg=color[1])
                        if hasattr(mod['module'], 'on_config_change'):
                            mod['module'].on_config_change(self, k, color[1])
                
                tk.Button(frame_color, text="Elegir Color", command=elegir_color,
                         bg='#6366f1', fg='#ffffff', font=('Arial', 8, 'bold'),
                         relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Botón cerrar
        btn_frame = tk.Frame(config_win, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✓ Cerrar", command=config_win.destroy,
                 bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 10, 'bold'),
                 relief='flat', cursor='hand2', width=15).pack()
    
    def ejecutar_mods_click(self, event):
        """Ejecuta la función on_click de los mods activos"""
        for mod_info in self.mods_cargados:
            if mod_info.get('activo', False):
                try:
                    mod = mod_info.get('module')
                    if mod and hasattr(mod, 'on_click'):
                        mod.on_click(self, event)
                except Exception as e:
                    print(f"Error en mod {mod_info.get('nombre', 'desconocido')} (on_click): {e}")
                    # Desactivar mod problemático
                    mod_info['activo'] = False
                    if 'var' in mod_info:
                        mod_info['var'].set(False)
    
    def ejecutar_mods_actualizar(self):
        """Ejecuta la función actualizar de los mods activos"""
        for mod_info in self.mods_cargados:
            if mod_info.get('activo', False):
                try:
                    mod = mod_info.get('module')
                    if mod and hasattr(mod, 'actualizar'):
                        mod.actualizar(self)
                except Exception as e:
                    print(f"Error en mod {mod_info.get('nombre', 'desconocido')} (actualizar): {e}")
                    # Desactivar mod problemático
                    mod_info['activo'] = False
                    if 'var' in mod_info:
                        mod_info['var'].set(False)
                    self.mostrar_texto(f"⚠️ Mod {mod_info.get('nombre', 'desconocido')} desactivado por error")
    
    def editor_frases(self):
        editor = tk.Toplevel(self.root)
        editor.title("Editor de Frases")
        editor.geometry("400x400")
        editor.configure(bg='#1e1e2e')
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                editor.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(editor, text="Frases Personalizadas", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=10)
        
        frame_lista = tk.Frame(editor, bg='#1e1e2e')
        frame_lista.pack(pady=10, fill='both', expand=True, padx=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, bg='#313244', fg='#cdd6f4', font=('Arial', 9))
        for frase in self.frases:
            listbox.insert(tk.END, frase)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        def agregar():
            nueva = simpledialog.askstring("Nueva Frase", "Escribe la nueva frase:")
            if nueva:
                self.frases.append(nueva)
                listbox.insert(tk.END, nueva)
        
        def eliminar():
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                self.frases.pop(idx)
                listbox.delete(idx)
        
        btn_frame = tk.Frame(editor, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Agregar", command=agregar, bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Eliminar", command=eliminar, bg='#f38ba8', fg='#1e1e2e', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
    
    def guardar_config(self):
        config = {
            'tamano': self.tamano,
            'opacidad': self.opacidad,
            'rotacion': self.rotacion,
            'frases': self.frases,
            'trail_color': self.trail_color,
            'sonido_path': self.sonido_path,
            'imagen_path': self.imagen_path
        }
        try:
            with open('config_mascota.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.cambios_sin_guardar = False
            messagebox.showinfo("Guardado", "Configuración guardada exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def cargar_config(self):
        try:
            with open('config_mascota.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.tamano = config.get('tamano', 100)
            self.opacidad = config.get('opacidad', 1.0)
            self.rotacion = config.get('rotacion', 0)
            self.frases = config.get('frases', self.frases)
            self.trail_color = config.get('trail_color', '#89b4fa')
            self.sonido_path = config.get('sonido_path', self.sonido_path)
            self.imagen_path = config.get('imagen_path', self.imagen_path)
            self.cargar_imagen()
            self.label.config(image=self.imagen)
            messagebox.showinfo("Cargado", "Configuración cargada exitosamente")
        except FileNotFoundError:
            messagebox.showwarning("Aviso", "No se encontró archivo de configuración")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar: {e}")
    
    def guardar_datos_juego(self):
        """Guarda todos los datos del juego en assets/data/save_data.json"""
        try:
            datos = {
                'version': '1.0',
                'mods_activos': {},
                'estadisticas': {
                    'clicks_totales': self.click_contador,
                    'distancia_recorrida': int(self.distancia_recorrida),
                    'tiempo_jugado': int(time.time() - self.tiempo_inicio),
                    'historial_clicks': len(self.historial_clicks)
                },
                'configuracion': {
                    'tamano': self.tamano,
                    'velocidad': abs(self.vel_x),
                    'opacidad': self.opacidad,
                    'rotacion': self.rotacion,
                    'imagen_path': self.imagen_path,
                    'sonido_path': self.sonido_path,
                    'musica_path': self.musica_path,
                    'trail_color': self.trail_color
                },
                'configuracion_avanzada': {
                    'max_clones': self.max_clones,
                    'zoom_direccion': self.zoom_direccion,
                    'escala_x': self.escala_x,
                    'escala_y': self.escala_y,
                    'angulo_rotacion': self.angulo_rotacion,
                    'gif_duracion': self.gif_duracion if self.es_gif else 100,
                    'es_gif': self.es_gif
                },
                'progreso': {
                    'nivel': self.nivel,
                    'experiencia': self.experiencia,
                    'logros': self.logros,
                    'inventario': self.inventario,
                    'hambre': int(self.hambre),
                    'felicidad': int(self.felicidad),
                    'estado_animo': self.estado_animo
                },
                'modos_activos': {
                    'rebote': self.rebote,
                    'gravedad': self.gravedad,
                    'trail_enabled': self.trail_enabled,
                    'sonido_enabled': self.sonido_enabled,
                    'modo_invisible': self.modo_invisible,
                    'modo_perseguir': self.modo_perseguir,
                    'zoom_auto': self.zoom_auto,
                    'rebote_elastico': self.rebote_elastico,
                    'rebote_elastico_aumentar': self.rebote_elastico_aumentar,
                    'particulas_mover': self.particulas_mover,
                    'modo_espejo_h': self.modo_espejo_h,
                    'modo_espejo_v': self.modo_espejo_v,
                    'modo_orbital': self.modo_orbital,
                    'modo_zigzag': self.modo_zigzag,
                    'modo_teletransporte': self.modo_teletransporte,
                    'musica_fondo': self.musica_fondo,
                    'sonidos_eventos': self.sonidos_eventos,
                    'modo_screensaver': self.modo_screensaver,
                    'clima_modo': self.clima_modo,
                    'rotacion_auto': self.rotacion_auto,
                    'rotar_al_rebotar': self.rotar_al_rebotar,
                    'sentido_rotacion': self.sentido_rotacion,
                    'explosion_random': self.explosion_random,
                    'modo_bordes': self.modo_bordes,
                    'modo_drunk': self.modo_drunk,
                    'sync_clones': self.sync_clones,
                    'rebote_loco': self.rebote_loco,
                    'modo_fantasma': self.modo_fantasma,
                    'modo_espiral': self.modo_espiral,
                    'modo_ladron': self.modo_ladron,
                    'modo_ruleta': self.modo_ruleta,
                    'modo_arcoiris': self.modo_arcoiris,
                    'modo_iman': self.modo_iman,
                    'modo_paparazzi': self.modo_paparazzi,
                    'modo_francotirador': self.modo_francotirador,
                    'modo_graffiti': self.modo_graffiti,
                    'modo_tornado': self.modo_tornado,
                    'modo_camaleon': self.modo_camaleon,
                    'camaleon_imagenes': self.camaleon_imagenes,
                    'modo_spam': self.modo_spam,
                    'modo_dormir': self.modo_dormir,
                    'modo_circo': self.modo_circo,
                    'modo_dados': self.modo_dados,
                    'modo_repeler': self.modo_repeler,
                    'modo_bailarin': self.modo_bailarin,
                    'bailarin_musica': self.bailarin_musica,
                    'modo_huir': self.modo_huir,
                    'arrastre_habilitado': self.arrastre_habilitado
                },
                'estados_modos': {
                    'espiral_angulo': self.espiral_angulo,
                    'espiral_radio': self.espiral_radio,
                    'tornado_angulo': self.tornado_angulo,
                    'tornado_velocidad': self.tornado_velocidad,
                    'arcoiris_hue': self.arcoiris_hue,
                    'angulo_orbital': self.angulo_orbital,
                    'centro_orbital_x': self.centro_orbital_x,
                    'centro_orbital_y': self.centro_orbital_y,
                    'borde_actual': self.borde_actual,
                    'zigzag_contador': self.zigzag_contador,
                    'camaleon_indice': self.camaleon_indice
                },
                'posicion_actual': {
                    'x': int(self.x),
                    'y': int(self.y),
                    'vel_x': self.vel_x,
                    'vel_y': self.vel_y,
                    'vel_gravedad': self.vel_gravedad
                },
                'timestamps': {
                    'ultimo_click': self.ultimo_click_tiempo,
                    'ultimo_hambre': self.ultimo_hambre,
                    'ultimo_interaccion': self.ultimo_interaccion,
                    'ladron_ultimo_robo': self.ladron_ultimo_robo,
                    'ruleta_ultimo': self.ruleta_ultimo,
                    'paparazzi_ultimo': self.paparazzi_ultimo,
                    'francotirador_ultimo': self.francotirador_ultimo,
                    'camaleon_ultimo': self.camaleon_ultimo,
                    'spam_ultimo': self.spam_ultimo,
                    'circo_ultimo': self.circo_ultimo,
                    'dados_ultimo': self.dados_ultimo
                },
                'experimental': {
                    'exp_nivel_agresion': self.exp_nivel_agresion,
                    'exp_hardcore': self.exp_hardcore,
                    'exp_ultrahardcore': self.exp_ultrahardcore
                },
                'preferencias': {
                    'pagina_favorita': self.pagina_actual,
                    'clima_actual': self.clima_actual,
                    'durmiendo': self.durmiendo
                },
                'frases_personalizadas': self.frases,
                'clones': {
                    'cantidad': len(self.clones),
                    'max_clones': self.max_clones
                },
                'clones_detallados': [
                    {
                        'x': int(clon['x']),
                        'y': int(clon['y']),
                        'vel_x': clon['vel_x'],
                        'vel_y': clon['vel_y']
                    } for clon in self.clones
                ]
            }
            
            # Guardar mods activos
            for mod in self.mods_cargados:
                if mod.get('activo', False):
                    datos['mods_activos'][mod.get('nombre', 'desconocido')] = True
            
            # Crear carpeta si no existe
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando datos: {e}")
    
    def cargar_datos_juego(self):
        """Carga todos los datos del juego desde assets/data/save_data.json"""
        try:
            if not os.path.exists(self.data_path):
                return
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.datos_guardados = json.load(f)
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.datos_guardados = {}
    
    def aplicar_datos_cargados(self):
        """Aplica los datos cargados al juego"""
        if not hasattr(self, 'datos_guardados'):
            return
        
        try:
            # Aplicar configuración
            if 'configuracion' in self.datos_guardados:
                cfg = self.datos_guardados['configuracion']
                self.tamano = cfg.get('tamano', 100)
                vel = cfg.get('velocidad', 3)
                self.vel_x = vel if self.vel_x > 0 else -vel
                self.vel_y = vel if self.vel_y > 0 else -vel
                self.opacidad = cfg.get('opacidad', 1.0)
                self.rotacion = cfg.get('rotacion', 0)
                if 'imagen_path' in cfg and os.path.exists(cfg['imagen_path']):
                    self.imagen_path = cfg['imagen_path']
                if 'sonido_path' in cfg:
                    self.sonido_path = cfg['sonido_path']
                if 'musica_path' in cfg:
                    self.musica_path = cfg['musica_path']
                if 'trail_color' in cfg:
                    self.trail_color = cfg['trail_color']
            
            # Aplicar configuración avanzada
            if 'configuracion_avanzada' in self.datos_guardados:
                cfg_adv = self.datos_guardados['configuracion_avanzada']
                self.max_clones = cfg_adv.get('max_clones', 10)
                self.zoom_direccion = cfg_adv.get('zoom_direccion', 1)
                self.escala_x = cfg_adv.get('escala_x', 1.0)
                self.escala_y = cfg_adv.get('escala_y', 1.0)
                self.angulo_rotacion = cfg_adv.get('angulo_rotacion', 0)
                self.gif_duracion = cfg_adv.get('gif_duracion', 100)
            
            # Aplicar progreso
            if 'progreso' in self.datos_guardados:
                prog = self.datos_guardados['progreso']
                self.nivel = prog.get('nivel', 1)
                self.experiencia = prog.get('experiencia', 0)
                self.logros = prog.get('logros', [])
                self.inventario = prog.get('inventario', [])
                self.hambre = prog.get('hambre', 100)
                self.felicidad = prog.get('felicidad', 100)
                self.estado_animo = prog.get('estado_animo', 'feliz')
            
            # Aplicar modos
            if 'modos_activos' in self.datos_guardados:
                modos = self.datos_guardados['modos_activos']
                self.rebote = modos.get('rebote', True)
                self.gravedad = modos.get('gravedad', False)
                self.trail_enabled = modos.get('trail_enabled', False)
                self.sonido_enabled = modos.get('sonido_enabled', False)
                self.modo_invisible = modos.get('modo_invisible', False)
                self.modo_perseguir = modos.get('modo_perseguir', False)
                self.zoom_auto = modos.get('zoom_auto', False)
                self.rebote_elastico = modos.get('rebote_elastico', False)
                self.rebote_elastico_aumentar = modos.get('rebote_elastico_aumentar', False)
                self.particulas_mover = modos.get('particulas_mover', False)
                self.modo_espejo_h = modos.get('modo_espejo_h', False)
                self.modo_espejo_v = modos.get('modo_espejo_v', False)
                self.modo_orbital = modos.get('modo_orbital', False)
                self.modo_zigzag = modos.get('modo_zigzag', False)
                self.modo_teletransporte = modos.get('modo_teletransporte', False)
                self.musica_fondo = modos.get('musica_fondo', False)
                self.sonidos_eventos = modos.get('sonidos_eventos', False)
                self.modo_screensaver = modos.get('modo_screensaver', False)
                self.clima_modo = modos.get('clima_modo', False)
                self.rotacion_auto = modos.get('rotacion_auto', False)
                self.rotar_al_rebotar = modos.get('rotar_al_rebotar', False)
                self.sentido_rotacion = modos.get('sentido_rotacion', 1)
                self.explosion_random = modos.get('explosion_random', False)
                self.modo_bordes = modos.get('modo_bordes', False)
                self.modo_drunk = modos.get('modo_drunk', False)
                self.sync_clones = modos.get('sync_clones', False)
                self.rebote_loco = modos.get('rebote_loco', False)
                self.modo_fantasma = modos.get('modo_fantasma', False)
                self.modo_espiral = modos.get('modo_espiral', False)
                self.modo_ladron = modos.get('modo_ladron', False)
                self.modo_ruleta = modos.get('modo_ruleta', False)
                self.modo_arcoiris = modos.get('modo_arcoiris', False)
                self.modo_iman = modos.get('modo_iman', False)
                self.modo_paparazzi = modos.get('modo_paparazzi', False)
                self.modo_francotirador = modos.get('modo_francotirador', False)
                self.modo_graffiti = modos.get('modo_graffiti', False)
                self.modo_tornado = modos.get('modo_tornado', False)
                self.modo_camaleon = modos.get('modo_camaleon', False)
                if 'camaleon_imagenes' in modos:
                    self.camaleon_imagenes = modos['camaleon_imagenes']
                self.modo_spam = modos.get('modo_spam', False)
                self.modo_dormir = modos.get('modo_dormir', False)
                self.modo_circo = modos.get('modo_circo', False)
                self.modo_dados = modos.get('modo_dados', False)
                self.modo_repeler = modos.get('modo_repeler', False)
                self.modo_bailarin = modos.get('modo_bailarin', False)
                if 'bailarin_musica' in modos:
                    self.bailarin_musica = modos['bailarin_musica']
                self.modo_huir = modos.get('modo_huir', False)
                self.arrastre_habilitado = modos.get('arrastre_habilitado', False)
            
            # Aplicar estados de modos
            if 'estados_modos' in self.datos_guardados:
                estados = self.datos_guardados['estados_modos']
                self.espiral_angulo = estados.get('espiral_angulo', 0)
                self.espiral_radio = estados.get('espiral_radio', 300)
                self.tornado_angulo = estados.get('tornado_angulo', 0)
                self.tornado_velocidad = estados.get('tornado_velocidad', 1)
                self.arcoiris_hue = estados.get('arcoiris_hue', 0)
                self.angulo_orbital = estados.get('angulo_orbital', 0)
                self.centro_orbital_x = estados.get('centro_orbital_x', 400)
                self.centro_orbital_y = estados.get('centro_orbital_y', 400)
                self.borde_actual = estados.get('borde_actual', 0)
                self.zigzag_contador = estados.get('zigzag_contador', 0)
                self.camaleon_indice = estados.get('camaleon_indice', 0)
            
            # Aplicar posición actual
            if 'posicion_actual' in self.datos_guardados:
                pos = self.datos_guardados['posicion_actual']
                self.x = pos.get('x', self.x)
                self.y = pos.get('y', self.y)
                self.vel_x = pos.get('vel_x', self.vel_x)
                self.vel_y = pos.get('vel_y', self.vel_y)
                self.vel_gravedad = pos.get('vel_gravedad', 0)
            
            # Aplicar timestamps
            if 'timestamps' in self.datos_guardados:
                ts = self.datos_guardados['timestamps']
                self.ultimo_click_tiempo = ts.get('ultimo_click', 0)
                self.ultimo_hambre = ts.get('ultimo_hambre', time.time())
                self.ultimo_interaccion = ts.get('ultimo_interaccion', time.time())
                self.ladron_ultimo_robo = ts.get('ladron_ultimo_robo', 0)
                self.ruleta_ultimo = ts.get('ruleta_ultimo', 0)
                self.paparazzi_ultimo = ts.get('paparazzi_ultimo', 0)
                self.francotirador_ultimo = ts.get('francotirador_ultimo', 0)
                self.camaleon_ultimo = ts.get('camaleon_ultimo', 0)
                self.spam_ultimo = ts.get('spam_ultimo', 0)
                self.circo_ultimo = ts.get('circo_ultimo', 0)
                self.dados_ultimo = ts.get('dados_ultimo', 0)
            
            # Aplicar experimental
            if 'experimental' in self.datos_guardados:
                exp = self.datos_guardados['experimental']
                self.exp_nivel_agresion = exp.get('exp_nivel_agresion', 0)
                self.exp_hardcore = exp.get('exp_hardcore', False)
                self.exp_ultrahardcore = exp.get('exp_ultrahardcore', False)
            
            # Aplicar preferencias
            if 'preferencias' in self.datos_guardados:
                pref = self.datos_guardados['preferencias']
                self.clima_actual = pref.get('clima_actual', 'soleado')
                self.durmiendo = pref.get('durmiendo', False)
            
            # Aplicar frases personalizadas
            if 'frases_personalizadas' in self.datos_guardados:
                self.frases = self.datos_guardados['frases_personalizadas']
            
            # Aplicar clones
            if 'clones' in self.datos_guardados:
                self.max_clones = self.datos_guardados['clones'].get('max_clones', 10)
            
            # Activar mods guardados
            if 'mods_activos' in self.datos_guardados:
                for mod in self.mods_cargados:
                    nombre = mod.get('nombre', 'desconocido')
                    if nombre in self.datos_guardados['mods_activos']:
                        mod['activo'] = True
                        if 'var' in mod:
                            mod['var'].set(True)
                        if hasattr(mod['module'], 'inicializar'):
                            try:
                                mod['module'].inicializar(self)
                            except Exception as e:
                                print(f"Error inicializando mod {nombre}: {e}")
        except Exception as e:
            print(f"Error aplicando datos: {e}")
    
    def crear_icono_tray(self):
        try:
            icono_img = Image.open(self.imagen_path)
            icono_img = icono_img.resize((64, 64), Image.Resampling.LANCZOS)
            menu = pystray.Menu(
                pystray.MenuItem("Mostrar", self.mostrar_ventana),
                pystray.MenuItem("Ocultar", self.ocultar_ventana),
                pystray.MenuItem("Pausar", self.pausar_tray),
                pystray.MenuItem("Salir", self.cerrar_desde_tray)
            )
            self.tray_icon = pystray.Icon("Ankush Cat", icono_img, "Ankush Cat", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Error tray: {e}")
    
    def mostrar_ventana(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
    
    def ocultar_ventana(self, icon=None, item=None):
        self.root.withdraw()
    
    def pausar_tray(self, icon=None, item=None):
        self.pausar()
    
    def cerrar_desde_tray(self, icon=None, item=None):
        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.stop()
        self.cerrar()
    
    def minimizar_a_tray(self):
        self.root.withdraw()
    
    def cerrar_con_confirmacion(self):
        self.guardar_datos_juego()
        dialog = tk.Toplevel(self.root)
        dialog.title("Cerrar")
        dialog.geometry("350x150")
        dialog.configure(bg="#1e1e2e")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        x = (dialog.winfo_screenwidth() - 350) // 2
        y = (dialog.winfo_screenheight() - 150) // 2
        dialog.geometry(f"350x150+{x}+{y}")
        tk.Label(dialog, text="¿Qué deseas hacer?", bg="#1e1e2e", fg="#89b4fa", font=("Arial", 12, "bold")).pack(pady=15)
        btn_frame = tk.Frame(dialog, bg="#1e1e2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Cerrar Completamente", command=lambda: [dialog.destroy(), self.cerrar()], bg="#f38ba8", fg="#1e1e2e", font=("Arial", 10, "bold"), width=18).pack(pady=5)
        tk.Button(btn_frame, text="Segundo Plano", command=lambda: [dialog.destroy(), self.minimizar_a_tray()], bg="#a6e3a1", fg="#1e1e2e", font=("Arial", 10, "bold"), width=18).pack(pady=5)
        tk.Button(btn_frame, text="Cancelar", command=dialog.destroy, bg="#6c7086", fg="#cdd6f4", font=("Arial", 10, "bold"), width=18).pack(pady=5)
        dialog.wait_window()
    
    def cerrar(self):
        try:
            # Detener animaciones
            self.activo = False
            
            # Limpiar rastros
            for ventana in self.trail_ventanas:
                try:
                    ventana.destroy()
                except:
                    pass
            self.trail_ventanas = []
            
            # Limpiar clones
            for clon in self.clones:
                try:
                    clon['ventana'].destroy()
                except:
                    pass
            
            # Destruir ventanas
            try:
                self.ventana_imagen.destroy()
            except:
                pass
            
            try:
                self.root.destroy()
            except:
                pass
        except:
            pass
        finally:
            # Cerrar completamente el programa
            os._exit(0)
    
    def mover(self):
        if self.activo and not self.explotando and not self.arrastrando and not self.banandose and not self.modo_cazar:
            old_x, old_y = self.x, self.y
            
            # Modo huir del cursor
            if self.modo_huir:
                mouse_x = self.root.winfo_pointerx()
                mouse_y = self.root.winfo_pointery()
                dx = self.x - mouse_x
                dy = self.y - mouse_y
                dist = (dx**2 + dy**2)**0.5
                
                if dist < 150:
                    if dist > 0:
                        self.x += dx / dist * 8
                        self.y += dy / dist * 8
                    self.mostrar_texto("No me toques!")
                else:
                    self.x += self.vel_x
                    self.y += self.vel_y
            
            # Modo bordes
            if self.modo_bordes:
                vel = abs(self.vel_x)
                if self.borde_actual == 0:  # Arriba
                    self.x += vel
                    self.y = 0
                    if self.x >= self.ancho_pantalla - self.tamano:
                        self.borde_actual = 1
                elif self.borde_actual == 1:  # Derecha
                    self.x = self.ancho_pantalla - self.tamano
                    self.y += vel
                    if self.y >= self.alto_pantalla - self.tamano:
                        self.borde_actual = 2
                elif self.borde_actual == 2:  # Abajo
                    self.x -= vel
                    self.y = self.alto_pantalla - self.tamano
                    if self.x <= 0:
                        self.borde_actual = 3
                elif self.borde_actual == 3:  # Izquierda
                    self.x = 0
                    self.y -= vel
                    if self.y <= 0:
                        self.borde_actual = 0
            # Modo espiral mejorado
            elif self.modo_espiral:
                self.espiral_angulo += 0.15
                if random.randint(1, 200) == 1:
                    self.espiral_radio = 300
                self.espiral_radio = max(50, self.espiral_radio - 0.8)
                centro_x = self.ancho_pantalla // 2
                centro_y = self.alto_pantalla // 2
                import math
                offset = math.sin(self.espiral_angulo * 2) * 50
                self.x = centro_x + (self.espiral_radio + offset) * math.cos(self.espiral_angulo) - self.tamano // 2
                self.y = centro_y + (self.espiral_radio + offset) * math.sin(self.espiral_angulo) - self.tamano // 2
                if self.espiral_angulo % 1 < 0.1:
                    self.ventana_imagen.attributes('-alpha', 0.5 + abs(math.sin(self.espiral_angulo)) * 0.5)
                if self.espiral_radio <= 50:
                    self.espiral_radio = 300
                    self.espiral_angulo = 0
            # Modo orbital
            elif self.modo_orbital:
                self.angulo_orbital += 0.05
                radio = 200
                self.x = self.centro_orbital_x + radio * random.uniform(0.8, 1.2) * (1 if random.random() > 0.5 else -1) * abs(self.vel_x) / 10
                self.y = self.centro_orbital_y + radio * random.uniform(0.8, 1.2) * (1 if random.random() > 0.5 else -1) * abs(self.vel_y) / 10
            # Modo zigzag
            elif self.modo_zigzag:
                self.x += self.vel_x
                self.zigzag_contador += 1
                if self.zigzag_contador % random.randint(20, 40) == 0:
                    self.vel_y = -self.vel_y * random.uniform(0.8, 1.2)
                    self.vel_x = self.vel_x * random.uniform(0.9, 1.1)
                self.y += self.vel_y
            # Modo teletransporte
            elif self.modo_teletransporte and random.randint(1, 200) == 1:
                self.x = random.randint(0, self.ancho_pantalla - self.tamano)
                self.y = random.randint(0, self.alto_pantalla - self.tamano)
            # Modo perseguir cursor
            elif self.modo_perseguir:
                mouse_x = self.root.winfo_pointerx()
                mouse_y = self.root.winfo_pointery()
                dx = mouse_x - self.x - self.tamano // 2
                dy = mouse_y - self.y - self.tamano // 2
                dist = (dx**2 + dy**2)**0.5
                if dist > 10:
                    velocidad = min(15, 3 + dist / 50)
                    self.x += dx / dist * velocidad
                    self.y += dy / dist * velocidad
                    if self.x < 50:
                        self.x += 10
                    elif self.x > self.ancho_pantalla - 50:
                        self.x -= 10
                    if self.y < 50:
                        self.y += 10
                    elif self.y > self.alto_pantalla - 50:
                        self.y -= 10
            elif self.gravedad:
                self.vel_gravedad += 0.5
                self.y += int(self.vel_gravedad)
                self.x += self.vel_x
                
                if self.y >= self.alto_pantalla - self.tamano:
                    self.y = self.alto_pantalla - self.tamano
                    if self.rebote:
                        if self.rebote_elastico:
                            self.vel_gravedad = -abs(self.vel_gravedad) * (1.1 if self.rebote_elastico_aumentar else 1.0)
                        else:
                            self.vel_gravedad = -self.vel_gravedad * 0.8
                    else:
                        self.vel_gravedad = 0
                    if self.rotar_al_rebotar:
                        self.rotacion = (self.rotacion + (45 * self.sentido_rotacion)) % 360
                        self.cargar_imagen()
                        self.label.config(image=self.imagen)
                    if self.sonidos_eventos and time.time() - self.ultimo_rebote_tiempo > 0.1:
                        self.ultimo_rebote_tiempo = time.time()
                        try:
                            sound = mixer.Sound(os.path.join("assets", "bounce.mp3"))
                            sound.play()
                        except:
                            pass
                    
                if self.x <= 0 or self.x >= self.ancho_pantalla - self.tamano:
                    self.vel_x = -self.vel_x
                    if self.rotar_al_rebotar:
                        self.rotacion = (self.rotacion + (45 * self.sentido_rotacion)) % 360
                        self.cargar_imagen()
                        self.label.config(image=self.imagen)
                    if self.sonidos_eventos and time.time() - self.ultimo_rebote_tiempo > 0.1:
                        self.ultimo_rebote_tiempo = time.time()
                        try:
                            sound = mixer.Sound(os.path.join("assets", "bounce.mp3"))
                            sound.play()
                        except:
                            pass
            else:
                self.x += self.vel_x
                self.y += self.vel_y
                
                # Modo drunk: añadir tambaleo
                if self.modo_drunk:
                    self.x += random.randint(-3, 3)
                    self.y += random.randint(-3, 3)
                    if random.randint(1, 20) == 1:
                        self.vel_x += random.randint(-2, 2)
                        self.vel_y += random.randint(-2, 2)
                
                if self.rebote:
                    if self.x <= 0 or self.x >= self.ancho_pantalla - self.tamano:
                        vel_abs = abs(self.vel_x)
                        if self.rebote_elastico and self.rebote_elastico_aumentar:
                            self.vel_x = -self.vel_x * 1.05
                        else:
                            self.vel_x = -vel_abs if self.vel_x > 0 else vel_abs
                        # Rebote loco: cambiar dirección aleatoria
                        if self.rebote_loco:
                            self.vel_x = random.randint(3, 10) * random.choice([-1, 1])
                            self.vel_y = random.randint(3, 10) * random.choice([-1, 1])
                        if self.rotar_al_rebotar:
                            self.rotacion = (self.rotacion + (45 * self.sentido_rotacion)) % 360
                            self.cargar_imagen()
                            self.label.config(image=self.imagen)
                        if self.sonidos_eventos and time.time() - self.ultimo_rebote_tiempo > 0.1:
                            self.ultimo_rebote_tiempo = time.time()
                            try:
                                sound = mixer.Sound(os.path.join("assets", "bounce.mp3"))
                                sound.play()
                            except:
                                pass
                    if self.y <= 0 or self.y >= self.alto_pantalla - self.tamano:
                        vel_abs = abs(self.vel_y)
                        if self.rebote_elastico and self.rebote_elastico_aumentar:
                            self.vel_y = -self.vel_y * 1.05
                        else:
                            self.vel_y = -vel_abs if self.vel_y > 0 else vel_abs
                        # Rebote loco: cambiar dirección aleatoria
                        if self.rebote_loco:
                            self.vel_x = random.randint(3, 10) * random.choice([-1, 1])
                            self.vel_y = random.randint(3, 10) * random.choice([-1, 1])
                        if self.rotar_al_rebotar:
                            self.rotacion = (self.rotacion + (45 * self.sentido_rotacion)) % 360
                            self.cargar_imagen()
                            self.label.config(image=self.imagen)
                        if self.sonidos_eventos and time.time() - self.ultimo_rebote_tiempo > 0.1:
                            self.ultimo_rebote_tiempo = time.time()
                            try:
                                sound = mixer.Sound(os.path.join("assets", "bounce.mp3"))
                                sound.play()
                            except:
                                pass
                else:
                    # Modo fantasma: atravesar paredes
                    if self.modo_fantasma:
                        if self.x < -self.tamano:
                            self.x = self.ancho_pantalla
                        elif self.x > self.ancho_pantalla:
                            self.x = -self.tamano
                        if self.y < -self.tamano:
                            self.y = self.alto_pantalla
                        elif self.y > self.alto_pantalla:
                            self.y = -self.tamano
                    else:
                        if self.x < -self.tamano:
                            self.x = self.ancho_pantalla
                        elif self.x > self.ancho_pantalla:
                            self.x = -self.tamano
                        if self.y < -self.tamano:
                            self.y = self.alto_pantalla
                        elif self.y > self.alto_pantalla:
                            self.y = -self.tamano
            
            # Modo Ladrón de Ventanas
            if self.modo_ladron and time.time() - self.ladron_ultimo_robo > random.randint(5, 15):
                self.robar_ventana_activa()
                self.ladron_ultimo_robo = time.time()
            
            # Modo Ruleta Rusa
            if self.modo_ruleta and time.time() - self.ruleta_ultimo > 30:
                self.ejecutar_ruleta_rusa()
                self.ruleta_ultimo = time.time()
            
            # Modo Arcoiris
            if self.modo_arcoiris:
                self.aplicar_efecto_arcoiris()
            
            # Modo Imán
            if self.modo_iman:
                self.atraer_ventanas()
            
            # Modo Paparazzi
            if self.modo_paparazzi and time.time() - self.paparazzi_ultimo > random.randint(10, 30):
                self.tomar_screenshot()
                self.paparazzi_ultimo = time.time()
            
            # Modo Francotirador
            if self.modo_francotirador and time.time() - self.francotirador_ultimo > random.randint(20, 40):
                self.cerrar_ventana_aleatoria()
                self.francotirador_ultimo = time.time()
            
            # Modo Tornado
            if self.modo_tornado:
                self.aplicar_tornado()
            
            # Modo Camaleón
            if self.modo_camaleon and time.time() - self.camaleon_ultimo > 5:
                self.cambiar_imagen_camaleon()
                self.camaleon_ultimo = time.time()
            
            # Modo Spam
            if self.modo_spam and time.time() - self.spam_ultimo > random.randint(3, 8):
                self.mostrar_notificacion_spam()
                self.spam_ultimo = time.time()
            
            # Modo Circo
            if self.modo_circo and time.time() - self.circo_ultimo > random.randint(8, 15):
                self.ejecutar_truco_circo()
                self.circo_ultimo = time.time()
            
            # Modo Dados
            if self.modo_dados and time.time() - self.dados_ultimo > 30:
                self.tirar_dado()
                self.dados_ultimo = time.time()
            
            # Modo Repeler
            if self.modo_repeler:
                self.repeler_ventanas()
            
            # Modo Bailarín
            if self.modo_bailarin:
                self.bailar()
            
            # Calcular distancia
            dist_movida = ((self.x - old_x)**2 + (self.y - old_y)**2)**0.5
            self.distancia_recorrida += dist_movida
            
            # Partículas al mover
            if self.particulas_mover and random.randint(1, 5) == 1:
                particula = {
                    'x': self.x + self.tamano // 2,
                    'y': self.y + self.tamano // 2,
                    'vida': 20,
                    'tipo': random.choice(['⭐', '❤️', '✨'])
                }
                self.particulas_lista.append(particula)
            
            # Rastro
            if self.trail_enabled:
                self.trail_positions.append((int(self.x), int(self.y)))
                if len(self.trail_positions) > 10:  # Límite de 10 imágenes
                    self.trail_positions.pop(0)
                self.dibujar_trail()
            
            # Modo invisible con fade
            if self.modo_invisible and random.randint(1, 150) == 1:
                try:
                    sound = mixer.Sound(os.path.join("assets", "teleport.mp3"))
                    sound.play()
                except:
                    pass
                def fade_out(alpha=1.0):
                    if alpha > 0:
                        self.ventana_imagen.attributes('-alpha', alpha)
                        self.root.after(50, lambda: fade_out(alpha - 0.1))
                    else:
                        self.ventana_imagen.withdraw()
                        self.root.after(random.randint(1000, 3000), fade_in)
                def fade_in(alpha=0.0):
                    if alpha < self.opacidad:
                        self.ventana_imagen.deiconify()
                        self.ventana_imagen.attributes('-alpha', alpha)
                        self.root.after(50, lambda: fade_in(alpha + 0.1))
                    else:
                        self.ventana_imagen.attributes('-alpha', self.opacidad)
                fade_out()
            
            # Explosión random
            if self.explosion_random and not self.explotando and random.randint(1, 500) == 1:
                self.explotar()
            
            # Zoom automático
            if self.zoom_auto:
                self.tamano += self.zoom_direccion * 2
                if self.tamano >= 200 or self.tamano <= 50:
                    self.zoom_direccion *= -1
                self.cargar_imagen()
                self.label.config(image=self.imagen)
            
            # Rotación automática
            if self.rotacion_auto:
                self.angulo_rotacion = (self.angulo_rotacion + 5) % 360
                if not self.es_gif:  # Solo recargar si no es GIF
                    self.cargar_imagen()
                    self.label.config(image=self.imagen)
            
            self.ventana_imagen.geometry(f"+{int(self.x)}+{int(self.y)}")
        
        # Ejecutar mods
        self.ejecutar_mods_actualizar()
        
        # Mover clones
        for clon in self.clones:
            if self.sync_clones:
                clon['x'] = self.x + random.randint(-50, 50)
                clon['y'] = self.y + random.randint(-50, 50)
            else:
                clon['x'] += clon['vel_x']
                clon['y'] += clon['vel_y']
                if clon['x'] <= 0 or clon['x'] >= self.ancho_pantalla - self.tamano:
                    clon['vel_x'] *= -1
                if clon['y'] <= 0 or clon['y'] >= self.alto_pantalla - self.tamano:
                    clon['vel_y'] *= -1
            try:
                clon['ventana'].geometry(f"+{int(clon['x'])}+{int(clon['y'])}")
            except:
                pass
        
        # Animar partículas
        self.particulas_lista = [p for p in self.particulas_lista if p['vida'] > 0]
        for p in self.particulas_lista:
            p['vida'] -= 1
        
        self.root.after(20, self.mover)
    
    def robar_ventana_activa(self):
        """Roba la ventana activa del usuario y la mueve a una posición aleatoria"""
        if not WIN32_AVAILABLE:
            return
        try:
            hwnd = win32gui.GetForegroundWindow()
            titulo = win32gui.GetWindowText(hwnd)
            
            # No robar la ventana del panel de control ni la mascota
            if "Control de Imagen Flotante" in titulo or not titulo:
                return
            
            # Obtener tamaño de la ventana
            rect = win32gui.GetWindowRect(hwnd)
            ancho = rect[2] - rect[0]
            alto = rect[3] - rect[1]
            
            # Nueva posición aleatoria
            nueva_x = random.randint(0, self.ancho_pantalla - ancho)
            nueva_y = random.randint(0, self.alto_pantalla - alto)
            
            # Mover ventana
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, nueva_x, nueva_y, ancho, alto, 0)
            
            frases_robo = [
                "Jajaja te robé la ventana!",
                "Ups, se movió tu ventana!",
                "Soy un ladrón de ventanas!",
                "No encuentras tu ventana? 😈",
                "Toma! *mueve ventana*"
            ]
            self.mostrar_texto(random.choice(frases_robo))
        except:
            pass
    
    def ejecutar_ruleta_rusa(self):
        opciones = ['explotar', 'clones', 'xp']
        resultado = random.choice(opciones)
        
        if resultado == 'explotar':
            self.mostrar_texto("💣 BOOM! Ruleta rusa!")
            self.root.after(1000, self.explotar)
        elif resultado == 'clones':
            self.mostrar_texto("👥 5 clones aparecen!")
            for i in range(5):
                self.root.after(i * 200, self.crear_clon_automatico)
        else:
            self.mostrar_texto("✨ +50 XP! Suerte!")
            self.ganar_experiencia(50)
    
    def crear_clon_automatico(self):
        """Crea un clon sin preguntar por imagen"""
        # Verificar límite de clones
        if len(self.clones) >= self.max_clones:
            print(f"⚠️ Límite de clones alcanzado ({self.max_clones})")
            return
        
        imagen_clon = self.imagen
        
        clon = tk.Toplevel(self.root)
        clon.overrideredirect(True)
        clon.attributes('-topmost', True)
        clon.attributes('-transparentcolor', 'white')
        clon.config(bg='white')
        
        # GUARDAR REFERENCIA EN EL CLON
        clon.imagen_ref = imagen_clon
        label_clon = tk.Label(clon, image=clon.imagen_ref, bg='white')
        label_clon.pack()
        
        x_clon = random.randint(0, self.ancho_pantalla - self.tamano)
        y_clon = random.randint(0, self.alto_pantalla - self.tamano)
        clon.geometry(f"+{x_clon}+{y_clon}")
        
        self.clones.append({'ventana': clon, 'x': x_clon, 'y': y_clon, 'vel_x': random.randint(-5, 5), 'vel_y': random.randint(-5, 5), 'imagen': imagen_clon})
    
    def aplicar_efecto_arcoiris(self):
        import colorsys
        from PIL import ImageEnhance, ImageFilter
        
        self.arcoiris_hue = (self.arcoiris_hue + 0.02) % 1.0
        
        try:
            # Cargar imagen original
            if self.es_gif:
                return  # No aplicar a GIFs para evitar lag
            
            img = Image.open(self.imagen_path)
            if self.modo_espejo_h:
                img = ImageOps.mirror(img)
            if self.modo_espejo_v:
                img = ImageOps.flip(img)
            
            ancho = int(self.tamano * self.escala_x)
            alto = int(self.tamano * self.escala_y)
            img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
            
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Aplicar tinte de color arcoiris
            rgb = colorsys.hsv_to_rgb(self.arcoiris_hue, 0.5, 1.0)
            overlay = Image.new('RGB', img.size, (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
            img = Image.blend(img, overlay, 0.3)
            
            if self.rotacion != 0 or self.rotacion_auto:
                angulo = self.rotacion + (self.angulo_rotacion if self.rotacion_auto else 0)
                img = img.rotate(angulo, expand=False)
            
            self.imagen = ImageTk.PhotoImage(img)
            self.label.config(image=self.imagen)
            if self.trail_enabled and random.randint(1, 3) == 1:
                particula = {
                    'x': self.x + self.tamano // 2,
                    'y': self.y + self.tamano // 2,
                    'vida': 15,
                    'tipo': random.choice(['✨', '⭐', '💫']),
                    'color': f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
                }
                self.particulas_lista.append(particula)
        except:
            pass
    
    def atraer_ventanas(self):
        if not WIN32_AVAILABLE:
            return
        try:
            def enum_callback(hwnd, ventanas):
                if win32gui.IsWindowVisible(hwnd):
                    titulo = win32gui.GetWindowText(hwnd)
                    if titulo and "Control de Imagen Flotante" not in titulo:
                        ventanas.append(hwnd)
            
            ventanas = []
            win32gui.EnumWindows(enum_callback, ventanas)
            
            for hwnd in ventanas[:5]:  # Solo primeras 5
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    x_ventana = rect[0]
                    y_ventana = rect[1]
                    ancho = rect[2] - rect[0]
                    alto = rect[3] - rect[1]
                    
                    # Mover hacia la mascota
                    dx = self.x - x_ventana
                    dy = self.y - y_ventana
                    dist = (dx**2 + dy**2)**0.5
                    
                    if dist > 100:
                        nueva_x = int(x_ventana + dx * 0.02)
                        nueva_y = int(y_ventana + dy * 0.02)
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, nueva_x, nueva_y, ancho, alto, 0)
                except:
                    pass
        except:
            pass
    
    def tomar_screenshot(self):
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/screenshot_{timestamp}.png"
            screenshot.save(filename)
            self.mostrar_texto(f"📸 Screenshot guardado!")
            try:
                sound = mixer.Sound(os.path.join("assets", "steam-screenshot-capture-sound-hurts-my-ears.mp3"))
                sound.play()
            except:
                pass
        except:
            pass
    
    def cerrar_ventana_aleatoria(self):
        if not WIN32_AVAILABLE:
            return
        try:
            def enum_callback(hwnd, ventanas):
                if win32gui.IsWindowVisible(hwnd):
                    titulo = win32gui.GetWindowText(hwnd)
                    if titulo and "Control de Imagen Flotante" not in titulo and "Python" not in titulo:
                        ventanas.append({'hwnd': hwnd, 'titulo': titulo})
            
            ventanas = []
            win32gui.EnumWindows(enum_callback, ventanas)
            
            if ventanas:
                ventana = random.choice(ventanas)
                self.mostrar_texto(f"🎯 Cerrando: {ventana['titulo'][:20]}...")
                self.root.after(3000, lambda: win32gui.PostMessage(ventana['hwnd'], 0x0010, 0, 0))
        except:
            pass
    
    def iniciar_graffiti(self):
        self.graffiti_activo = True
        self.graffiti_canvas = tk.Toplevel(self.root)
        self.graffiti_canvas.attributes('-fullscreen', True)
        self.graffiti_canvas.attributes('-topmost', True)
        self.graffiti_canvas.attributes('-alpha', 0.3)
        self.graffiti_canvas.config(bg='black')
        
        # Crear canvas para dibujar
        canvas = tk.Canvas(self.graffiti_canvas, bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        
        # Instrucciones
        instrucciones = tk.Label(self.graffiti_canvas, 
                                text="🎨 MODO GRAFFITI | Clic izq: Dibujar | Clic der: Cambiar color | ESC: Salir | C: Limpiar",
                                bg='black', fg='white', font=('Arial', 12, 'bold'))
        instrucciones.place(x=10, y=10)
        
        ultimo_x = [None]
        ultimo_y = [None]
        color_actual = ['#ff0000']
        grosor = [5]
        
        def dibujar(event):
            if ultimo_x[0] is not None and ultimo_y[0] is not None:
                canvas.create_line(ultimo_x[0], ultimo_y[0], event.x, event.y, 
                                 fill=color_actual[0], width=grosor[0], capstyle='round', smooth=True)
            ultimo_x[0] = event.x
            ultimo_y[0] = event.y
        
        def soltar(event):
            ultimo_x[0] = None
            ultimo_y[0] = None
        
        def cambiar_color(event):
            colores = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', 
                      '#ffffff', '#ffa500', '#ff1493', '#00ff7f']
            color_actual[0] = random.choice(colores)
            self.mostrar_texto(f"Color: {color_actual[0]}")
        
        def limpiar(event):
            canvas.delete('all')
            self.mostrar_texto("🧹 Canvas limpiado!")
        
        def salir(event):
            self.detener_graffiti()
        
        def aumentar_grosor(event):
            grosor[0] = min(20, grosor[0] + 2)
            self.mostrar_texto(f"Grosor: {grosor[0]}")
        
        def disminuir_grosor(event):
            grosor[0] = max(1, grosor[0] - 2)
            self.mostrar_texto(f"Grosor: {grosor[0]}")
        
        # Bindings
        canvas.bind('<B1-Motion>', dibujar)
        canvas.bind('<ButtonRelease-1>', soltar)
        canvas.bind('<Button-3>', cambiar_color)
        self.graffiti_canvas.bind('<Escape>', salir)
        self.graffiti_canvas.bind('c', limpiar)
        self.graffiti_canvas.bind('C', limpiar)
        self.graffiti_canvas.bind('+', aumentar_grosor)
        self.graffiti_canvas.bind('-', disminuir_grosor)
        
        self.graffiti_canvas.focus_set()
        self.mostrar_texto("🎨 Graffiti activado! ESC para salir")
    
    def detener_graffiti(self):
        if self.graffiti_canvas:
            self.graffiti_canvas.destroy()
            self.graffiti_canvas = None
        self.graffiti_activo = False
    
    def aplicar_tornado(self):
        import math
        self.tornado_angulo += 0.15 * self.tornado_velocidad
        self.tornado_velocidad = min(5, self.tornado_velocidad + 0.02)
        radio = 150 + abs(math.sin(self.tornado_angulo / 2)) * 100
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        self.x = centro_x + radio * math.cos(self.tornado_angulo) - self.tamano // 2
        self.y = centro_y + radio * math.sin(self.tornado_angulo) - self.tamano // 2
        
        for i, clon in enumerate(self.clones):
            angulo_clon = self.tornado_angulo + (i * 0.8)
            radio_clon = radio + (i * 40)
            clon['x'] = centro_x + radio_clon * math.cos(angulo_clon) - self.tamano // 2
            clon['y'] = centro_y + radio_clon * math.sin(angulo_clon) - self.tamano // 2
        if not WIN32_AVAILABLE:
            return
        try:
            def enum_callback(hwnd, ventanas):
                if win32gui.IsWindowVisible(hwnd):
                    titulo = win32gui.GetWindowText(hwnd)
                    if titulo and "Control" not in titulo:
                        ventanas.append(hwnd)
            ventanas = []
            win32gui.EnumWindows(enum_callback, ventanas)
            for hwnd in ventanas[:3]:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    x_v, y_v = rect[0], rect[1]
                    dx = centro_x - x_v
                    dy = centro_y - y_v
                    dist = (dx**2 + dy**2)**0.5
                    if dist < 400:
                        nueva_x = int(x_v + dx * 0.05)
                        nueva_y = int(y_v + dy * 0.05)
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, nueva_x, nueva_y, rect[2]-rect[0], rect[3]-rect[1], 0)
                except:
                    pass
        except:
            pass
    
    def cambiar_imagen_camaleon(self):
        if self.camaleon_imagenes:
            self.camaleon_indice = (self.camaleon_indice + 1) % len(self.camaleon_imagenes)
            self.imagen_path = self.camaleon_imagenes[self.camaleon_indice]
            self.es_gif = False
            self.gif_frames = []
            self.cargar_imagen()
            self.label.config(image=self.imagen)
            self.mostrar_texto(f"🎭 Imagen {self.camaleon_indice + 1}/{len(self.camaleon_imagenes)}")
    
    def mostrar_notificacion_spam(self):
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        notif.config(bg='#16202d')
        
        # Posición inicial (fuera de pantalla a la derecha)
        notif_width = 320
        notif_height = 90
        x_final = self.ancho_pantalla - notif_width - 20
        y_pos = self.alto_pantalla - 120 - (len(self.notificaciones) * 100)
        x_inicial = self.ancho_pantalla
        
        notif.geometry(f"{notif_width}x{notif_height}+{x_inicial}+{y_pos}")
        
        # Frame principal con borde estilo Steam
        main_frame = tk.Frame(notif, bg='#16202d', relief='flat')
        main_frame.pack(fill='both', expand=True)
        
        # Barra superior azul
        top_bar = tk.Frame(main_frame, bg='#1b2838', height=3)
        top_bar.pack(fill='x')
        
        # Contenido
        content_frame = tk.Frame(main_frame, bg='#16202d')
        content_frame.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Frame izquierdo para la imagen
        left_frame = tk.Frame(content_frame, bg='#16202d')
        left_frame.pack(side='left', padx=(0, 10))
        
        # Cargar y mostrar imagen de la mascota
        try:
            img_notif = Image.open(self.imagen_path)
            img_notif = img_notif.resize((60, 60), Image.Resampling.LANCZOS)
            img_notif_tk = ImageTk.PhotoImage(img_notif)
            img_label = tk.Label(left_frame, image=img_notif_tk, bg='#16202d')
            img_label.image = img_notif_tk  # Guardar referencia
            img_label.pack()
        except:
            # Si falla, mostrar emoji
            tk.Label(left_frame, text="🐱", bg='#16202d', fg='#66c0f4', 
                    font=('Arial', 40)).pack()
        
        # Frame derecho para el texto
        right_frame = tk.Frame(content_frame, bg='#16202d')
        right_frame.pack(side='left', fill='both', expand=True)
        
        mensajes = [
            "Ankush Cat te ha enviado un mensaje",
            "Nuevo logro desbloqueado!",
            "Tu mascota te extraña",
            "Tienes 1 notificación nueva",
            "Ankush Cat está jugando",
            "Invitación de amistad",
            "Nuevo objeto en inventario",
            "Ankush Cat está en línea",
            "Logro: Primer clon creado",
            "Ankush Cat quiere jugar"
        ]
        
        tk.Label(right_frame, text="Ankush Cat", bg='#16202d', fg='#66c0f4', 
                font=('Arial', 10, 'bold'), anchor='w').pack(fill='x')
        tk.Label(right_frame, text=random.choice(mensajes), bg='#16202d', fg='#c7d5e0', 
                font=('Arial', 8), wraplength=200, anchor='w', justify='left').pack(fill='x', pady=(2, 0))
        
        self.notificaciones.append(notif)
        
        # Reproducir sonido
        try:
            sound = mixer.Sound(os.path.join("assets", "steam_notification.mp3"))
            sound.play()
        except:
            pass
        
        # Animación de deslizamiento
        pasos = 20
        delay = 10
        
        def animar_entrada(paso=0):
            if paso < pasos:
                progreso = paso / pasos
                # Easing suave
                ease = 1 - (1 - progreso) ** 3
                x_actual = x_inicial + (x_final - x_inicial) * ease
                notif.geometry(f"{notif_width}x{notif_height}+{int(x_actual)}+{y_pos}")
                self.root.after(delay, lambda: animar_entrada(paso + 1))
            else:
                # Programar cierre después de 4 segundos
                self.root.after(4000, lambda: animar_salida())
        
        def animar_salida(paso=0):
            if paso < pasos:
                progreso = paso / pasos
                ease = progreso ** 3
                x_actual = x_final + (x_inicial - x_final) * ease
                try:
                    notif.geometry(f"{notif_width}x{notif_height}+{int(x_actual)}+{y_pos}")
                    self.root.after(delay, lambda: animar_salida(paso + 1))
                except:
                    pass
            else:
                cerrar_notif()
        
        def cerrar_notif():
            try:
                notif.destroy()
                if notif in self.notificaciones:
                    self.notificaciones.remove(notif)
            except:
                pass
        
        # Iniciar animación
        animar_entrada()
    
    def ejecutar_truco_circo(self):
        """Ejecuta un truco aleatorio del circo"""
        trucos = ['voltereta', 'desaparecer', 'multiplicarse']
        truco = random.choice(trucos)
        
        if truco == 'voltereta':
            self.mostrar_texto("🤸 ¡Voltereta!")
            # Voltereta animada con rotación suave
            def animar_voltereta(paso=0):
                if paso < 4:
                    self.rotacion = (self.rotacion + 90) % 360
                    self.cargar_imagen()
                    self.label.config(image=self.imagen)
                    self.root.after(150, lambda: animar_voltereta(paso + 1))
            animar_voltereta()
        elif truco == 'desaparecer':
            self.mostrar_texto("👻 ¡Desaparezco!")
            self.ventana_imagen.withdraw()
            self.root.after(2000, lambda: self.ventana_imagen.deiconify())
        else:  # multiplicarse
            self.mostrar_texto("👥 ¡Me multiplico!")
            for _ in range(3):
                self.crear_clon_automatico()
    
    def tirar_dado(self):
        """Tira un dado y ejecuta acción según el número"""
        numero = random.randint(1, 6)
        dado_win = tk.Toplevel(self.root)
        dado_win.overrideredirect(True)
        dado_win.attributes('-topmost', True)
        dado_win.config(bg='#1e1e2e')
        x = (self.ancho_pantalla - 200) // 2
        y = (self.alto_pantalla - 200) // 2
        dado_win.geometry(f"200x200+{x}+{y}")
        canvas = tk.Canvas(dado_win, width=200, height=200, bg='#1e1e2e', highlightthickness=0)
        canvas.pack()
        caras = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        resultado = [numero]
        def animar_dado(frame=0):
            if frame < 20:
                canvas.delete('all')
                cara_actual = caras[random.randint(0, 5)]
                size = 80 + abs(10 - frame) * 2
                canvas.create_text(100, 100, text=cara_actual, font=('Arial', size), fill='#89b4fa')
                self.root.after(50, lambda: animar_dado(frame + 1))
            else:
                canvas.delete('all')
                canvas.create_text(100, 100, text=caras[resultado[0] - 1], font=('Arial', 100), fill='#a6e3a1')
                self.root.after(1000, lambda: [dado_win.destroy(), ejecutar_accion()])
        def ejecutar_accion():
            numero = resultado[0]
            acciones = {
            1: ("⚡ Velocidad x2", lambda: setattr(self, 'vel_x', self.vel_x * 2) or setattr(self, 'vel_y', self.vel_y * 2)),
            2: ("👥 3 clones", lambda: [self.crear_clon_automatico() for _ in range(3)]),
            3: ("🌈 Arcoiris ON", lambda: setattr(self, 'modo_arcoiris', True) or self.arcoiris_var.set(True)),
            4: ("💥 Explosión", lambda: self.explotar()),
            5: ("✨ +50 XP", lambda: self.ganar_experiencia(50)),
            6: ("🎁 Teletransporte", lambda: setattr(self, 'x', random.randint(0, self.ancho_pantalla - self.tamano)) or setattr(self, 'y', random.randint(0, self.alto_pantalla - self.tamano)))
        }
        
            texto, accion = acciones[numero]
            self.mostrar_texto(f"🎲 Dado: {numero} - {texto}")
            accion()
        animar_dado()
    
    def repeler_ventanas(self):
        """Empuja las ventanas lejos de la mascota"""
        if not WIN32_AVAILABLE:
            return
        try:
            def enum_callback(hwnd, ventanas):
                if win32gui.IsWindowVisible(hwnd):
                    titulo = win32gui.GetWindowText(hwnd)
                    if titulo and "Control de Imagen Flotante" not in titulo:
                        ventanas.append(hwnd)
            
            ventanas = []
            win32gui.EnumWindows(enum_callback, ventanas)
            
            for hwnd in ventanas[:5]:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    x_ventana = rect[0]
                    y_ventana = rect[1]
                    ancho = rect[2] - rect[0]
                    alto = rect[3] - rect[1]
                    
                    # Empujar lejos de la mascota
                    dx = x_ventana - self.x
                    dy = y_ventana - self.y
                    dist = (dx**2 + dy**2)**0.5
                    
                    if dist < 300 and dist > 0:
                        nueva_x = int(x_ventana + dx / dist * 10)
                        nueva_y = int(y_ventana + dy / dist * 10)
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, nueva_x, nueva_y, ancho, alto, 0)
                except:
                    pass
        except:
            pass
    
    def bailar(self):
        """Hace que la mascota baile al ritmo de la música"""
        try:
            if mixer.music.get_busy():
                pos = mixer.music.get_pos()
                beat_interval = 400
                current_beat = (pos // beat_interval) % 8
                
                # Movimientos más dinámicos
                if current_beat == 0:
                    # Beat fuerte - salto grande + giro
                    self.y -= 20
                    self.rotacion = (self.rotacion + 90) % 360
                    if not self.es_gif:
                        self.cargar_imagen()
                        self.label.config(image=self.imagen)
                elif current_beat == 2:
                    self.y -= 12
                    self.x += 8
                elif current_beat == 4:
                    self.y -= 20
                    self.rotacion = (self.rotacion - 90) % 360
                    if not self.es_gif:
                        self.cargar_imagen()
                        self.label.config(image=self.imagen)
                elif current_beat == 6:
                    self.y -= 12
                    self.x -= 8
                else:
                    # Volver suavemente
                    if self.y < self.alto_pantalla - 150:
                        self.y += 8
                
                # Movimiento ondulante
                import math
                self.x += int(math.sin(pos / 100) * 5)
            else:
                # Baile simple sin música
                self.bailarin_beat = (self.bailarin_beat + 1) % 20
                if self.bailarin_beat % 4 == 0:
                    self.y -= 10
                elif self.bailarin_beat % 4 == 2:
                    self.y += 10
                if self.bailarin_beat < 10:
                    self.x += 3
                else:
                    self.x -= 3
        except:
            self.bailarin_beat = (self.bailarin_beat + 1) % 20
            if self.bailarin_beat % 4 == 0:
                self.y -= 10
            elif self.bailarin_beat % 4 == 2:
                self.y += 10
    
    def dibujar_trail(self):
        # Ajustar número de ventanas existentes
        num_necesarias = len(self.trail_positions) - 1
        
        # Crear ventanas faltantes con tiempo de vida
        while len(self.trail_ventanas) < num_necesarias:
            trail_win = tk.Toplevel(self.root)
            trail_win.overrideredirect(True)
            trail_win.attributes('-topmost', False)
            trail_win.attributes('-transparentcolor', 'white')
            trail_win.attributes('-alpha', 0.2)
            trail_win.config(bg='white')
            
            # Crear copia de la imagen con referencia fuerte
            try:
                # Guardar referencia en el objeto trail_win
                trail_win.imagen_ref = self.imagen
                label_trail = tk.Label(trail_win, image=trail_win.imagen_ref, bg='white')
                label_trail.pack()
            except:
                trail_win.destroy()
                continue
            
            trail_win.tiempo_creacion = time.time()
            self.trail_ventanas.append(trail_win)
            
            # Destruir después de 500ms
            def destruir_trail(ventana=trail_win):
                try:
                    if ventana in self.trail_ventanas:
                        self.trail_ventanas.remove(ventana)
                    ventana.destroy()
                except:
                    pass
            self.root.after(500, destruir_trail)
        
        # Eliminar ventanas sobrantes
        while len(self.trail_ventanas) > num_necesarias:
            try:
                self.trail_ventanas.pop().destroy()
            except:
                pass
        
        # Actualizar posiciones y opacidad
        for i, (tx, ty) in enumerate(self.trail_positions[:-1]):
            try:
                if i < len(self.trail_ventanas):
                    ventana = self.trail_ventanas[i]
                    ventana.geometry(f"+{tx}+{ty}")
                    edad = time.time() - ventana.tiempo_creacion
                    opacidad = max(0.05, 0.3 - (edad * 0.4))
                    ventana.attributes('-alpha', opacidad)
            except:
                pass
    
    def jugar_ppt(self):
        opciones = ["Piedra", "Papel", "Tijera"]
        eleccion_usuario = simpledialog.askstring("Piedra Papel Tijera", "Elige: Piedra, Papel o Tijera")
        if not eleccion_usuario:
            return
        eleccion_usuario = eleccion_usuario.capitalize()
        if eleccion_usuario not in opciones:
            messagebox.showerror("Error", "Opción inválida")
            return
        
        eleccion_mascota = random.choice(opciones)
        resultado = ""
        
        if eleccion_usuario == eleccion_mascota:
            resultado = f"Empate! Ambos eligieron {eleccion_usuario}"
        elif (eleccion_usuario == "Piedra" and eleccion_mascota == "Tijera") or \
             (eleccion_usuario == "Papel" and eleccion_mascota == "Piedra") or \
             (eleccion_usuario == "Tijera" and eleccion_mascota == "Papel"):
            resultado = f"Ganaste! {eleccion_usuario} vence a {eleccion_mascota}"
            self.ganar_experiencia(20)
            self.agregar_item("Trofeo PPT")
        else:
            resultado = f"Perdiste! {eleccion_mascota} vence a {eleccion_usuario}"
            self.felicidad = min(100, self.felicidad + 5)
        
        messagebox.showinfo("Resultado", resultado)
        self.mostrar_texto(resultado)
    
    def iniciar_atrapar(self):
        self.modo_perseguir = False
        self.perseguir_var.set(False)
        self.activo = True
        self.vel_x = random.randint(8, 15) * random.choice([-1, 1])
        self.vel_y = random.randint(8, 15) * random.choice([-1, 1])
        self.mostrar_texto("Intenta atraparme!")
        
        intentos = [0]
        tiempo_inicio = time.time()
        
        def click_atrapar(event):
            intentos[0] += 1
            if intentos[0] == 1:
                self.mostrar_texto("Casi!")
            elif intentos[0] == 2:
                self.mostrar_texto("Soy muy rápido!")
            elif intentos[0] >= 3:
                tiempo_total = time.time() - tiempo_inicio
                self.label.unbind('<Button-1>')
                self.label.bind('<Button-1>', self.on_click)
                self.vel_x = 3 if self.vel_x > 0 else -3
                self.vel_y = 3 if self.vel_y > 0 else -3
                messagebox.showinfo("Atrapado!", f"Me atrapaste en {intentos[0]} intentos y {tiempo_total:.1f} segundos!")
                self.ganar_experiencia(30)
                self.agregar_item("Medalla Cazador")
                self.felicidad = min(100, self.felicidad + 15)
        
        self.label.unbind('<Button-1>')
        self.label.bind('<Button-1>', click_atrapar)
    
    def toggle_huir(self):
        self.modo_huir = self.huir_var.get()
    
    def ganar_experiencia(self, cantidad):
        self.experiencia += cantidad
        while self.experiencia >= 100:
            self.experiencia -= 100
            self.nivel += 1
            messagebox.showinfo("Nivel Up!", f"Subiste al nivel {self.nivel}!")
            self.verificar_logros()
    
    def agregar_item(self, item):
        self.inventario.append(item)
        self.verificar_logros()
    
    def verificar_logros(self):
        if self.nivel >= 5 and "Nivel 5" not in self.logros:
            self.logros.append("Nivel 5")
            messagebox.showinfo("Logro!", "Desbloqueaste: Nivel 5")
        if self.click_contador >= 100 and "100 Clicks" not in self.logros:
            self.logros.append("100 Clicks")
            messagebox.showinfo("Logro!", "Desbloqueaste: 100 Clicks")
        if len(self.inventario) >= 5 and "Coleccionista" not in self.logros:
            self.logros.append("Coleccionista")
            messagebox.showinfo("Logro!", "Desbloqueaste: Coleccionista")
    
    def ver_inventario(self):
        inv_win = tk.Toplevel(self.root)
        inv_win.title("Inventario")
        inv_win.geometry("300x400")
        inv_win.configure(bg='#1e1e2e')
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                inv_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(inv_win, text="🎒 Inventario", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=10)
        
        if not self.inventario:
            tk.Label(inv_win, text="Inventario vacío", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10)).pack(pady=20)
        else:
            frame = tk.Frame(inv_win, bg='#1e1e2e')
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side='right', fill='y')
            listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, bg='#313244', fg='#cdd6f4', font=('Arial', 9))
            for item in self.inventario:
                listbox.insert(tk.END, item)
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
    
    def ver_logros(self):
        logros_win = tk.Toplevel(self.root)
        logros_win.title("Logros")
        logros_win.geometry("300x400")
        logros_win.configure(bg='#1e1e2e')
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                logros_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(logros_win, text="🏆 Logros", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=10)
        
        if not self.logros:
            tk.Label(logros_win, text="Aún no hay logros", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10)).pack(pady=20)
        else:
            frame = tk.Frame(logros_win, bg='#1e1e2e')
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side='right', fill='y')
            listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, bg='#313244', fg='#cdd6f4', font=('Arial', 9))
            for logro in self.logros:
                listbox.insert(tk.END, f"⭐ {logro}")
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
    
    def toggle_hardcore(self):
        if self.hardcore_var.get():
            self.ultrahardcore_var.set(False)
            self.exp_ultrahardcore = False
            respuesta = messagebox.askyesno(
                "🔥 MODO HARDCORE 🔥",
                "Estás seguro de activar el MODO HARDCORE?\n\n⚠️ ADVERTENCIA ⚠️\n\n• Daño de la mascota: 10 HP por hit\n• Daño de clones: 10 HP por hit\n• Velocidad aumentada x2\n• Más clones\n• Grab más frecuente\n\nEsto es EXTREMADAMENTE difícil!"
            )
            if not respuesta:
                self.hardcore_var.set(False)
                self.exp_hardcore = False
            else:
                self.exp_hardcore = True
                messagebox.showwarning("🔥 HARDCORE ACTIVADO 🔥", "Que Dios te ayude...")
        else:
            self.exp_hardcore = False
    
    def toggle_ultrahardcore(self):
        if self.ultrahardcore_var.get():
            self.hardcore_var.set(False)
            self.exp_hardcore = False
            respuesta = messagebox.askyesno(
                "💀 MODO ULTRA HARDCORE 💀",
                "ESTÁS COMPLETAMENTE SEGURO?\n\n☠️ ADVERTENCIA EXTREMA ☠️\n\n• Daño de la mascota: 50 HP por hit\n• Daño de clones: 50 HP por hit\n• Velocidad aumentada x3\n• MUCHOS más clones\n• Grab MUCHO más frecuente\n\nEsto es PRÁCTICAMENTE IMPOSIBLE!\n\n¿Continuar?"
            )
            if not respuesta:
                self.ultrahardcore_var.set(False)
                self.exp_ultrahardcore = False
            else:
                self.exp_ultrahardcore = True
                messagebox.showerror("💀 ULTRA HARDCORE ACTIVADO 💀", "Ni Dios puede salvarte ahora...")
        else:
            self.exp_ultrahardcore = False
    
    def jugar_adivina_ventana(self):
        self.activo = False
        
        if self.usar_ventanas_reales_var.get():
            # Modo con ventanas reales - MUEVE LAS VENTANAS DEL USUARIO
            import win32gui
            import win32process
            import psutil
            
            # Obtener ventanas abiertas del usuario
            def enum_windows_callback(hwnd, ventanas):
                if win32gui.IsWindowVisible(hwnd):
                    titulo = win32gui.GetWindowText(hwnd)
                    if titulo and titulo != "Control de Imagen Flotante" and "Python" not in titulo:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            proceso = psutil.Process(pid)
                            if proceso.username() == f"{os.environ.get('USERDOMAIN', '')}\\{getpass.getuser()}":
                                ventanas.append({'hwnd': hwnd, 'titulo': titulo})
                        except:
                            pass
            
            ventanas_usuario = []
            win32gui.EnumWindows(enum_windows_callback, ventanas_usuario)
            
            if len(ventanas_usuario) < 3:
                messagebox.showwarning("Pocas ventanas", "Necesitas al menos 3 ventanas abiertas para jugar!")
                self.activo = True
                return
            
            # Seleccionar hasta 6 ventanas aleatorias
            num_ventanas = min(6, len(ventanas_usuario))
            ventanas_seleccionadas = random.sample(ventanas_usuario, num_ventanas)
            ventana_correcta = random.randint(0, num_ventanas - 1)
            juego_activo = [True]
            
            # Ocultar mascota principal
            self.ventana_imagen.withdraw()
            
            # Guardar posiciones originales y crear datos de movimiento
            ventanas_juego = []
            for i, v in enumerate(ventanas_seleccionadas):
                try:
                    rect = win32gui.GetWindowRect(v['hwnd'])
                    x_orig = rect[0]
                    y_orig = rect[1]
                    ancho_orig = rect[2] - rect[0]
                    alto_orig = rect[3] - rect[1]
                    
                    # Redimensionar ventana a tamaño pequeño (150x100)
                    win32gui.SetWindowPos(v['hwnd'], None, 0, 0, 150, 100, 0x0002 | 0x0004)
                    
                    # Posición inicial aleatoria
                    x_pos = random.randint(100, self.ancho_pantalla - 300)
                    y_pos = random.randint(100, self.alto_pantalla - 300)
                    
                    ventanas_juego.append({
                        'hwnd': v['hwnd'],
                        'titulo': v['titulo'],
                        'indice': i,
                        'x': x_pos,
                        'y': y_pos,
                        'x_orig': x_orig,
                        'y_orig': y_orig,
                        'ancho_orig': ancho_orig,
                        'alto_orig': alto_orig,
                        'vel_x': random.uniform(-3, 3),
                        'vel_y': random.uniform(-3, 3)
                    })
                except:
                    pass
            
            def animar_ventanas_reales():
                if not juego_activo[0]:
                    return
                
                for v in ventanas_juego:
                    # Actualizar posición
                    v['x'] += v['vel_x']
                    v['y'] += v['vel_y']
                    
                    # Rebotes en bordes
                    if v['x'] <= 0 or v['x'] >= self.ancho_pantalla - 200:
                        v['vel_x'] *= -1
                    if v['y'] <= 0 or v['y'] >= self.alto_pantalla - 150:
                        v['vel_y'] *= -1
                    
                    # Mover ventana real
                    try:
                        win32gui.SetWindowPos(v['hwnd'], None, int(v['x']), int(v['y']), 0, 0, 0x0001 | 0x0004)
                    except:
                        pass
                
                self.root.after(30, animar_ventanas_reales)
            
            def elegir_ventana(indice):
                juego_activo[0] = False
                
                # Cerrar panel de selección
                juego_win.destroy()
                
                # Restaurar posiciones y tamaños originales
                for v in ventanas_juego:
                    try:
                        win32gui.SetWindowPos(v['hwnd'], None, v['x_orig'], v['y_orig'], v['ancho_orig'], v['alto_orig'], 0x0004)
                    except:
                        pass
                
                # Mostrar mascota principal
                self.ventana_imagen.deiconify()
                
                if indice == ventana_correcta:
                    try:
                        sound = mixer.Sound(os.path.join("assets", "true.mp3"))
                        sound.play()
                    except:
                        pass
                    messagebox.showinfo("✅ ¡CORRECTO!", f"¡Encontraste a la mascota!\n\nEstaba en: {ventanas_seleccionadas[indice]['titulo']}\n\n+50 XP\n+20 Felicidad")
                    self.ganar_experiencia(50)
                    self.felicidad = min(100, self.felicidad + 20)
                    self.agregar_item("Trofeo Adivino")
                    self.mostrar_texto("¡Me encontraste!")
                else:
                    try:
                        sound = mixer.Sound(os.path.join("assets", "wrong.mp3"))
                        sound.play()
                    except:
                        pass
                    ventana_a_cerrar = random.choice(ventanas_seleccionadas)
                    try:
                        win32gui.PostMessage(ventana_a_cerrar['hwnd'], 0x0010, 0, 0)
                        messagebox.showwarning("❌ Fallaste", f"No estaba ahí...\n\nCASTIGO: Se cerró la ventana:\n{ventana_a_cerrar['titulo']}")
                        self.mostrar_texto("Jajaja perdiste una ventana!")
                    except:
                        messagebox.showinfo("❌ Fallaste", "No estaba ahí, pero no pude cerrar la ventana...")
                
                self.activo = True
            
            # Crear botones para elegir
            juego_win = tk.Toplevel(self.root)
            juego_win.title("🎰 Adivina la Ventana")
            juego_win.geometry("600x150")
            juego_win.configure(bg='#1e1e2e')
            juego_win.attributes('-topmost', True)
            juego_win.resizable(False, False)
            
            x = (self.ancho_pantalla - 600) // 2
            y = 50
            juego_win.geometry(f"600x150+{x}+{y}")
            
            tk.Label(juego_win, text="🎰 ADIVINA LA VENTANA 🎰", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 14, 'bold')).pack(pady=10)
            tk.Label(juego_win, text="Ankush está escondido en una de tus ventanas. ¡Haz clic en el botón correcto!", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10)).pack(pady=5)
            tk.Label(juego_win, text="⚠️ Si fallas, se cerrará una ventana aleatoria!", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 9, 'bold')).pack(pady=5)
            
            btn_frame = tk.Frame(juego_win, bg='#1e1e2e')
            btn_frame.pack(pady=10)
            
            for i in range(num_ventanas):
                titulo_corto = ventanas_seleccionadas[i]['titulo'][:15] + "..." if len(ventanas_seleccionadas[i]['titulo']) > 15 else ventanas_seleccionadas[i]['titulo']
                tk.Button(btn_frame, text=titulo_corto, command=lambda idx=i: elegir_ventana(idx),
                         bg='#89b4fa', fg='#1e1e2e', font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=3)
            
            animar_ventanas_reales()
        else:
            # Modo seguro: ventanas flotantes con Ankush escondido
            import math
            
            num_ventanas = random.randint(4, 6)
            ventana_correcta = random.randint(0, num_ventanas - 1)
            ventanas_juego = []
            juego_activo = [True]
            
            # Ocultar mascota principal
            self.ventana_imagen.withdraw()
            
            # Crear ventanas flotantes
            for i in range(num_ventanas):
                ventana = tk.Toplevel(self.root)
                ventana.overrideredirect(True)
                ventana.attributes('-topmost', True)
                ventana.config(bg='#313244')
                
                frame = tk.Frame(ventana, bg='#313244', relief='solid', bd=2)
                frame.pack(padx=3, pady=3)
                
                # TODAS las ventanas tienen el mismo signo "?" del mismo color - MÁS PEQUEÑAS
                canvas = tk.Canvas(frame, width=60, height=60, bg='#45475a', highlightthickness=0)
                canvas.pack()
                canvas.create_text(30, 30, text="?", font=('Arial', 30, 'bold'), fill='#89b4fa')
                
                # Guardar referencia a la imagen solo en la correcta (pero no se muestra)
                if i == ventana_correcta:
                    ventana.ankush_img = self.imagen
                
                # Posición y velocidad aleatoria
                x_pos = random.randint(100, self.ancho_pantalla - 100)
                y_pos = random.randint(100, self.alto_pantalla - 100)
                
                ventanas_juego.append({
                    'ventana': ventana,
                    'indice': i,
                    'x': x_pos,
                    'y': y_pos,
                    'vel_x': random.uniform(-4, 4),
                    'vel_y': random.uniform(-4, 4),
                    'angulo': random.uniform(0, 360),
                    'vel_angular': random.uniform(-2, 2)
                })
                
                # Bind de clic en la ventana
                def hacer_clic(event, idx=i):
                    elegir_ventana(idx)
                
                ventana.bind('<Button-1>', hacer_clic)
                frame.bind('<Button-1>', hacer_clic)
                canvas.bind('<Button-1>', hacer_clic)
            
            def animar_ventanas():
                if not juego_activo[0]:
                    return
                
                for v in ventanas_juego:
                    # Actualizar posición
                    v['x'] += v['vel_x']
                    v['y'] += v['vel_y']
                    
                    # Rebotes en bordes
                    if v['x'] <= 0 or v['x'] >= self.ancho_pantalla - 80:
                        v['vel_x'] *= -1
                    if v['y'] <= 0 or v['y'] >= self.alto_pantalla - 80:
                        v['vel_y'] *= -1
                    
                    # Actualizar ángulo de rotación
                    v['angulo'] += v['vel_angular']
                    
                    try:
                        v['ventana'].geometry(f"+{int(v['x'])}+{int(v['y'])}")
                    except:
                        pass
                
                self.root.after(30, animar_ventanas)
            
            def elegir_ventana(indice):
                juego_activo[0] = False
                
                # Destruir todas las ventanas
                for v in ventanas_juego:
                    try:
                        v['ventana'].destroy()
                    except:
                        pass
                
                # Mostrar mascota principal
                self.ventana_imagen.deiconify()
                
                if indice == ventana_correcta:
                    try:
                        sound = mixer.Sound(os.path.join("assets", "true.mp3"))
                        sound.play()
                    except:
                        pass
                    messagebox.showinfo("✅ ¡CORRECTO!", "¡Encontraste a la mascota!\n\n+50 XP\n+20 Felicidad")
                    self.ganar_experiencia(50)
                    self.felicidad = min(100, self.felicidad + 20)
                    self.agregar_item("Trofeo Adivino")
                    self.mostrar_texto("¡Me encontraste!")
                else:
                    try:
                        sound = mixer.Sound(os.path.join("assets", "wrong.mp3"))
                        sound.play()
                    except:
                        pass
                    messagebox.showinfo("❌ Fallaste", "No estaba ahí...\n\nLa mascota se escapó!")
                    self.mostrar_texto("Jajaja no me atrapaste!")
                    self.x = random.randint(0, self.ancho_pantalla - self.tamano)
                    self.y = random.randint(0, self.alto_pantalla - self.tamano)
                
                self.activo = True
            
            animar_ventanas()
    
    def boton_experimental(self):
        respuesta = messagebox.askyesno(
            "⚠️ ADVERTENCIA EXPERIMENTAL ⚠️",
            "Estás seguro? Esto es EXPERIMENTAL y puede ser peligroso!\n\nLa mascota te perseguirá y te quitará HP."
        )
        if respuesta:
            self.iniciar_modo_cazar()
    
    def iniciar_modo_cazar(self):
        self.modo_cazar = True
        self.cazar_activo = True
        self.cazar_inicio = time.time()
        self.cazar_hp = 100
        self.exp_nivel_agresion = 0
        self.exp_velocidad_base = 7
        self.exp_invisible_activo = False
        self.exp_grab_activo = False
        self.exp_ultimo_hit = 0
        
        try:
            mixer.music.load(os.path.join("assets", "videoplayback.mp3"))
            mixer.music.play(0)  # Reproducir solo una vez (0 = no loop)
        except:
            pass
        
        try:
            sound = mixer.Sound(os.path.join("assets", "ready-or-not-here-i-come.mp3"))
            sound.play()
        except:
            pass
        
        self.mostrar_texto("Ready or not, here I come!")
        
        self.ventana_hp = tk.Toplevel(self.root)
        self.ventana_hp.title("HP")
        self.ventana_hp.geometry("250x180")
        self.ventana_hp.configure(bg='#1e1e2e')
        self.ventana_hp.attributes('-topmost', True)
        
        tk.Label(self.ventana_hp, text="❤️ HP del Ratón", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 12, 'bold')).pack(pady=5)
        self.hp_label = tk.Label(self.ventana_hp, text=f"HP: {self.cazar_hp}/100", bg='#1e1e2e', fg='#a6e3a1', font=('Arial', 14, 'bold'))
        self.hp_label.pack(pady=5)
        self.tiempo_label = tk.Label(self.ventana_hp, text="Tiempo: 1:30", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold'))
        self.tiempo_label.pack(pady=5)
        self.agresion_label = tk.Label(self.ventana_hp, text="Nivel: 0", bg='#1e1e2e', fg='#f9e2af', font=('Arial', 10, 'bold'))
        self.agresion_label.pack(pady=3)
        
        self.actualizar_cazar()
    
    def actualizar_cazar(self):
        if not self.cazar_activo:
            return
        
        tiempo_transcurrido = time.time() - self.cazar_inicio
        tiempo_restante = 95 - tiempo_transcurrido
        
        if tiempo_transcurrido >= 95:
            self.terminar_cazar(True)
            return
        
        # Sistema de agresión progresiva
        nuevo_nivel = int(tiempo_transcurrido // 15)  # Cada 15 segundos
        if nuevo_nivel > self.exp_nivel_agresion and nuevo_nivel <= 6:
            self.exp_nivel_agresion = nuevo_nivel
            self.aumentar_agresion_experimental()
        
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        try:
            self.tiempo_label.config(text=f"Tiempo: {minutos}:{segundos:02d}")
            self.agresion_label.config(text=f"Nivel: {self.exp_nivel_agresion} | Vel: {int(self.exp_velocidad_base + (self.exp_nivel_agresion * 1.5))}")
        except:
            pass
        
        # Si está en grab, solo actualizar timer y HP, no perseguir
        if self.exp_grab_activo:
            self.root.after(50, self.actualizar_cazar)
            return
        
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        # Guardar historial de posiciones del ratón para predicción
        self.exp_posiciones_raton.append((mouse_x, mouse_y, time.time()))
        if len(self.exp_posiciones_raton) > 10:
            self.exp_posiciones_raton.pop(0)
        
        dx = mouse_x - self.x - self.tamano // 2
        dy = mouse_y - self.y - self.tamano // 2
        dist = (dx**2 + dy**2)**0.5
        
        # Velocidad aumenta con nivel de agresión
        if self.exp_ultrahardcore:
            velocidad = (self.exp_velocidad_base + (self.exp_nivel_agresion * 1.5)) * 3.0
        elif self.exp_hardcore:
            velocidad = (self.exp_velocidad_base + (self.exp_nivel_agresion * 1.5)) * 2.0
        else:
            velocidad = self.exp_velocidad_base + (self.exp_nivel_agresion * 1.5)
        
        # Modo invisible aleatorio en niveles altos
        if self.exp_nivel_agresion >= 3 and random.randint(1, 100) == 1:
            self.activar_invisible_temporal()
        
        # IA estratégica según dificultad
        if dist > 10 and not self.exp_invisible_activo:
            if self.exp_ultrahardcore:
                # Ultra Hardcore: Predicción avanzada + corte de camino
                if len(self.exp_posiciones_raton) >= 3:
                    # Calcular velocidad y dirección del ratón
                    pos_actual = self.exp_posiciones_raton[-1]
                    pos_anterior = self.exp_posiciones_raton[-3]
                    vel_raton_x = (pos_actual[0] - pos_anterior[0]) / (pos_actual[2] - pos_anterior[2] + 0.001)
                    vel_raton_y = (pos_actual[1] - pos_anterior[1]) / (pos_actual[2] - pos_anterior[2] + 0.001)
                    
                    # Predecir posición futura (0.5 segundos adelante)
                    pred_x = mouse_x + vel_raton_x * 0.5
                    pred_y = mouse_y + vel_raton_y * 0.5
                    
                    # Limitar predicción a pantalla
                    pred_x = max(0, min(self.ancho_pantalla, pred_x))
                    pred_y = max(0, min(self.alto_pantalla, pred_y))
                    
                    # Moverse hacia posición predicha
                    dx_pred = pred_x - self.x - self.tamano // 2
                    dy_pred = pred_y - self.y - self.tamano // 2
                    dist_pred = (dx_pred**2 + dy_pred**2)**0.5
                    
                    if dist_pred > 0:
                        self.x += dx_pred / dist_pred * velocidad
                        self.y += dy_pred / dist_pred * velocidad
                else:
                    # Persecución directa
                    self.x += dx / dist * velocidad
                    self.y += dy / dist * velocidad
            elif self.exp_hardcore:
                # Hardcore: Predicción básica
                if len(self.exp_posiciones_raton) >= 2:
                    pos_actual = self.exp_posiciones_raton[-1]
                    pos_anterior = self.exp_posiciones_raton[-2]
                    vel_raton_x = (pos_actual[0] - pos_anterior[0]) / (pos_actual[2] - pos_anterior[2] + 0.001)
                    vel_raton_y = (pos_actual[1] - pos_anterior[1]) / (pos_actual[2] - pos_anterior[2] + 0.001)
                    
                    # Predecir posición futura (0.3 segundos adelante)
                    pred_x = mouse_x + vel_raton_x * 0.3
                    pred_y = mouse_y + vel_raton_y * 0.3
                    
                    dx_pred = pred_x - self.x - self.tamano // 2
                    dy_pred = pred_y - self.y - self.tamano // 2
                    dist_pred = (dx_pred**2 + dy_pred**2)**0.5
                    
                    if dist_pred > 0:
                        self.x += dx_pred / dist_pred * velocidad
                        self.y += dy_pred / dist_pred * velocidad
                else:
                    self.x += dx / dist * velocidad
                    self.y += dy / dist * velocidad
            else:
                # Normal: Persecución directa simple
                self.x += dx / dist * velocidad
                self.y += dy / dist * velocidad
        
        # Sistema de daño mejorado (evitar spam)
        if dist < 50 and time.time() - self.exp_ultimo_hit > 0.5:
            if self.exp_ultrahardcore:
                dano = (1 + self.exp_nivel_agresion) * 50
            elif self.exp_hardcore:
                dano = (1 + self.exp_nivel_agresion) * 10
            else:
                dano = 1 + self.exp_nivel_agresion
            self.cazar_hp -= dano
            self.exp_ultimo_hit = time.time()
            
            try:
                sound = mixer.Sound(os.path.join("assets", "2011x-hit.mp3"))
                sound.play()
            except:
                pass
            
            self.hp_label.config(text=f"HP: {self.cazar_hp}/100")
            if self.cazar_hp <= 50:
                self.hp_label.config(fg='#f9e2af')
            if self.cazar_hp <= 20:
                self.hp_label.config(fg='#f38ba8')
            
            # Sistema de GRAB en niveles altos
            if self.exp_ultrahardcore:
                grab_chance = 2
            elif self.exp_hardcore:
                grab_chance = 3
            else:
                grab_chance = 5
            
            if self.exp_nivel_agresion >= 4 and random.randint(1, grab_chance) == 1:
                self.iniciar_grab()
            
            if self.cazar_hp <= 0:
                self.terminar_cazar(False)
                return
        
        if not self.exp_invisible_activo:
            self.ventana_imagen.geometry(f"+{int(self.x)}+{int(self.y)}")
        
        # Actualizar clones saltarines
        self.actualizar_clones_experimentales()
        
        self.root.after(50, self.actualizar_cazar)
    
    def terminar_cazar(self, sobrevivio):
        self.cazar_activo = False
        self.modo_cazar = False
        
        # Limpiar clones experimentales
        for clon in self.exp_clones_saltarines:
            try:
                clon['ventana'].destroy()
            except:
                pass
        self.exp_clones_saltarines = []
        
        # Solo detener música si NO sobrevivió
        if not sobrevivio:
            try:
                mixer.music.stop()
            except:
                pass
        
        if self.ventana_hp:
            self.ventana_hp.destroy()
            self.ventana_hp = None
        
        if sobrevivio:
            # No detener la música, dejarla sonar
            messagebox.showinfo("🎉 SOBREVIVISTE! 🎉", "Felicidades! Sobreviviste 1 minuto 35 segundos al modo experimental!\n\nLa música seguirá sonando como celebración.")
            self.ganar_experiencia(50)
            self.agregar_item("Medalla Supervivencia")
            self.mostrar_texto("Eres muy bueno!")
            # Activar rebote clásico
            self.rebote = True
            self.rebote_var.set(True)
            self.vel_x = random.randint(5, 10) * random.choice([-1, 1])
            self.vel_y = random.randint(5, 10) * random.choice([-1, 1])
        else:
            try:
                sound = mixer.Sound(os.path.join("assets", "reaadyornot.mp3"))
                sound.play()
            except:
                pass
            
            messagebox.showinfo("Game Over", "Te atrapé! El programa se cerrará...")
            self.root.after(2000, self.cerrar)
    
    def aumentar_agresion_experimental(self):
        nivel = self.exp_nivel_agresion
        
        mensajes = [
            "😈 Me estoy calentando...",
            "🔥 Nivel 2! Más rápido!",
            "⚡ Nivel 3! Puedo volverme invisible!",
            "💥 Nivel 4! GRAB ACTIVADO!",
            "💀 Nivel 5! MÁS CLONES!",
            "🔴 NIVEL MÁXIMO! IMPOSIBLE ESCAPAR!"
        ]
        
        if nivel <= len(mensajes):
            self.mostrar_texto(mensajes[nivel - 1])
        
        # Crear clon saltarin
        if nivel >= 2:
            self.crear_clon_experimental()
            if self.exp_hardcore:
                self.crear_clon_experimental()
            if self.exp_ultrahardcore:
                self.crear_clon_experimental()
                self.crear_clon_experimental()
        
        # Más clones en niveles altos
        if nivel >= 5:
            self.crear_clon_experimental()
            self.crear_clon_experimental()
            if self.exp_hardcore:
                self.crear_clon_experimental()
            if self.exp_ultrahardcore:
                self.crear_clon_experimental()
                self.crear_clon_experimental()
    
    def crear_clon_experimental(self):
        clon = tk.Toplevel(self.root)
        clon.overrideredirect(True)
        clon.attributes('-topmost', True)
        clon.attributes('-transparentcolor', 'white')
        clon.config(bg='white')
        
        # Usar imagen alternativa aleatoriamente
        imagen_clon = self.imagen
        if random.randint(1, 2) == 1 and os.path.exists(os.path.join("assets", "Ankushbiendespierto.png")):
            try:
                img_alt = Image.open(os.path.join("assets", "Ankushbiendespierto.png"))
                img_alt = img_alt.resize((self.tamano, self.tamano), Image.Resampling.LANCZOS)
                imagen_clon = ImageTk.PhotoImage(img_alt)
            except:
                imagen_clon = self.imagen
        
        label_clon = tk.Label(clon, image=imagen_clon, bg='white')
        label_clon.pack()
        
        # Decidir tipo de clon: 50% saltarin, 50% rebotador
        tipo_clon = random.choice(['saltarin', 'rebotador'])
        
        # Velocidad de clones aumentada en modos difíciles
        if self.exp_ultrahardcore:
            vel_mult = 2.0
        elif self.exp_hardcore:
            vel_mult = 1.5
        else:
            vel_mult = 1.0
        
        if tipo_clon == 'saltarin':
            x_clon = random.randint(0, self.ancho_pantalla - self.tamano)
            y_clon = self.alto_pantalla - self.tamano
            self.exp_clones_saltarines.append({
                'ventana': clon,
                'x': x_clon,
                'y': y_clon,
                'vel_x': int(random.randint(5, 10) * vel_mult) * random.choice([-1, 1]),
                'vel_y': 0,
                'en_salto': False,
                'salto_contador': random.randint(0, 30),
                'imagen': imagen_clon,
                'tipo': 'saltarin'
            })
        else:
            x_clon = random.randint(0, self.ancho_pantalla - self.tamano)
            y_clon = random.randint(0, self.alto_pantalla - self.tamano)
            self.exp_clones_saltarines.append({
                'ventana': clon,
                'x': x_clon,
                'y': y_clon,
                'vel_x': int(random.randint(5, 10) * vel_mult) * random.choice([-1, 1]),
                'vel_y': int(random.randint(5, 10) * vel_mult) * random.choice([-1, 1]),
                'imagen': imagen_clon,
                'tipo': 'rebotador'
            })
    
    def actualizar_clones_experimentales(self):
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        for clon in self.exp_clones_saltarines:
            if clon['tipo'] == 'saltarin':
                # Movimiento horizontal
                clon['x'] += clon['vel_x']
                
                # Rebotes en bordes
                if clon['x'] <= 0 or clon['x'] >= self.ancho_pantalla - self.tamano:
                    clon['vel_x'] *= -1
                
                # Sistema de salto
                if not clon['en_salto']:
                    clon['salto_contador'] += 1
                    if clon['salto_contador'] >= 30:
                        clon['en_salto'] = True
                        clon['vel_y'] = -20
                        clon['salto_contador'] = 0
                else:
                    clon['vel_y'] += 1.2
                    clon['y'] += clon['vel_y']
                    
                    if clon['y'] >= self.alto_pantalla - self.tamano:
                        clon['y'] = self.alto_pantalla - self.tamano
                        clon['en_salto'] = False
                        clon['vel_y'] = 0
            else:  # rebotador
                # Movimiento en ambas direcciones
                clon['x'] += clon['vel_x']
                clon['y'] += clon['vel_y']
                
                # Rebotes en todos los bordes
                if clon['x'] <= 0 or clon['x'] >= self.ancho_pantalla - self.tamano:
                    clon['vel_x'] *= -1
                if clon['y'] <= 0 or clon['y'] >= self.alto_pantalla - self.tamano:
                    clon['vel_y'] *= -1
            
            # Sistema de daño por contacto con clones
            dx = mouse_x - clon['x'] - self.tamano // 2
            dy = mouse_y - clon['y'] - self.tamano // 2
            dist = (dx**2 + dy**2)**0.5
            
            if dist < 50 and time.time() - self.exp_ultimo_hit > 0.5:
                if self.exp_ultrahardcore:
                    dano_clon = 50
                elif self.exp_hardcore:
                    dano_clon = 10
                else:
                    dano_clon = 3
                self.cazar_hp -= dano_clon
                self.exp_ultimo_hit = time.time()
                try:
                    sound = mixer.Sound(os.path.join("assets", "2011x-hit.mp3"))
                    sound.play()
                except:
                    pass
                self.hp_label.config(text=f"HP: {self.cazar_hp}/100")
                if self.cazar_hp <= 0:
                    self.terminar_cazar(False)
                    return
            
            # Actualizar posición visual
            try:
                clon['ventana'].geometry(f"+{int(clon['x'])}+{int(clon['y'])}")
            except:
                pass
    
    def activar_invisible_temporal(self):
        if self.exp_invisible_activo:
            return
        
        self.exp_invisible_activo = True
        self.ventana_imagen.withdraw()
        self.mostrar_texto("👻 No me ves...")
        
        # Reaparecer después de 2-4 segundos
        tiempo_invisible = random.randint(2000, 4000)
        self.root.after(tiempo_invisible, self.desactivar_invisible)
    
    def desactivar_invisible(self):
        self.exp_invisible_activo = False
        self.ventana_imagen.deiconify()
    
    def iniciar_grab(self):
        self.exp_grab_activo = True
        
        # Generar combinación aleatoria de teclas
        teclas_posibles = ['w', 'a', 's', 'd', 'q', 'e']
        self.exp_combo_objetivo = [random.choice(teclas_posibles) for _ in range(4)]
        self.exp_combo_teclas = []
        
        # Crear ventana de grab
        self.ventana_grab = tk.Toplevel(self.root)
        self.ventana_grab.title("⚠️ GRAB!")
        self.ventana_grab.geometry("400x250")
        self.ventana_grab.configure(bg='#f38ba8')
        self.ventana_grab.attributes('-topmost', True)
        self.ventana_grab.resizable(False, False)
        
        # Centrar ventana
        x = (self.ancho_pantalla - 400) // 2
        y = (self.alto_pantalla - 250) // 2
        self.ventana_grab.geometry(f"400x250+{x}+{y}")
        
        tk.Label(self.ventana_grab, text="👾 TE ATRAPÉ! 👾", bg='#f38ba8', fg='#1e1e2e', font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(self.ventana_grab, text="Escribe la combinación para escapar:", bg='#f38ba8', fg='#1e1e2e', font=('Arial', 11)).pack(pady=5)
        
        combo_text = ' - '.join([t.upper() for t in self.exp_combo_objetivo])
        tk.Label(self.ventana_grab, text=combo_text, bg='#1e1e2e', fg='#f9e2af', font=('Arial', 20, 'bold'), padx=20, pady=10).pack(pady=10)
        
        self.grab_progreso_label = tk.Label(self.ventana_grab, text="Progreso: ", bg='#f38ba8', fg='#1e1e2e', font=('Arial', 12, 'bold'))
        self.grab_progreso_label.pack(pady=10)
        
        tk.Label(self.ventana_grab, text="¡RÁPIDO! Pierdes 1 HP cada segundo", bg='#f38ba8', fg='#1e1e2e', font=('Arial', 9)).pack(pady=5)
        
        # Bind de teclas
        self.ventana_grab.bind('<Key>', self.procesar_tecla_grab)
        self.ventana_grab.focus_force()
        
        # Iniciar daño por tiempo
        self.dano_grab_activo = True
        self.aplicar_dano_grab()
    
    def procesar_tecla_grab(self, event):
        tecla = event.char.lower()
        
        if len(self.exp_combo_teclas) < len(self.exp_combo_objetivo):
            if tecla == self.exp_combo_objetivo[len(self.exp_combo_teclas)]:
                self.exp_combo_teclas.append(tecla)
                progreso = ' - '.join([t.upper() for t in self.exp_combo_teclas])
                self.grab_progreso_label.config(text=f"Progreso: {progreso}")
                
                # Comprobar si completó la combinación
                if len(self.exp_combo_teclas) == len(self.exp_combo_objetivo):
                    self.escapar_grab()
            else:
                # Tecla incorrecta, reiniciar
                self.exp_combo_teclas = []
                self.grab_progreso_label.config(text="Progreso: ❌ REINICIADO")
                self.cazar_hp -= 5
                self.hp_label.config(text=f"HP: {self.cazar_hp}/100")
    
    def aplicar_dano_grab(self):
        if not self.dano_grab_activo or not self.exp_grab_activo:
            return
        
        self.cazar_hp -= 1
        self.hp_label.config(text=f"HP: {self.cazar_hp}/100")
        
        if self.cazar_hp <= 0:
            self.dano_grab_activo = False
            self.terminar_cazar(False)
            return
        
        self.root.after(1000, self.aplicar_dano_grab)
    
    def escapar_grab(self):
        self.exp_grab_activo = False
        self.dano_grab_activo = False
        
        if self.ventana_grab:
            self.ventana_grab.destroy()
            self.ventana_grab = None
        
        self.mostrar_texto("✅ Escapaste!")
        
        # Teletransportar lejos
        self.x = random.randint(0, self.ancho_pantalla - self.tamano)
        self.y = random.randint(0, self.alto_pantalla - self.tamano)
    
    def mostrar_error_archivos_faltantes(self):
        """Muestra un mensaje de error amigable cuando faltan archivos"""
        error_win = tk.Toplevel(self.root)
        error_win.title("⚠️ Error de Archivos")
        error_win.geometry("500x400")
        error_win.configure(bg='#1e1e2e')
        error_win.resizable(False, False)
        error_win.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                error_win.iconbitmap(self.icon_path)
        except:
            pass
        
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        error_win.geometry(f"500x400+{x}+{y}")
        
        tk.Label(error_win, text="⚠️ ARCHIVOS FALTANTES ⚠️", bg='#1e1e2e', fg='#f38ba8',
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        mensaje_frame = tk.Frame(error_win, bg='#313244', relief='solid', bd=2)
        mensaje_frame.pack(pady=10, padx=30, fill='both', expand=True)
        
        mensaje = """\nNo se encontraron los archivos necesarios\npara ejecutar el programa.\n\n📁 Archivos requeridos:\n\n• assets/AnkushCat.png (o AnkushCat.gif)\n• assets/icon.ico\n• assets/sonidito.mp3\n• assets/Music.mp3\n• assets/bounce.mp3\n\n🛠️ Solución:\n\n1. Asegúrate de que la carpeta 'assets'\n   exista en el mismo directorio que\n   el programa.\n\n2. Verifica que todos los archivos\n   estén dentro de la carpeta 'assets'.\n\n3. Vuelve a ejecutar el programa.\n"""
        
        tk.Label(mensaje_frame, text=mensaje, bg='#313244', fg='#cdd6f4',
                 font=('Arial', 10), justify='left').pack(pady=20, padx=20)
        
        tk.Button(error_win, text="Cerrar", command=error_win.destroy, bg='#f38ba8', fg='#1e1e2e',
                 font=('Arial', 11, 'bold'), width=15, relief='flat', cursor='hand2').pack(pady=15)
    
    # ===== NUEVAS FUNCIONALIDADES =====
    
    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        acerca = tk.Toplevel(self.root)
        acerca.title("Acerca de")
        acerca.geometry("400x500")
        acerca.configure(bg='#1e1e2e')
        acerca.resizable(False, False)
        acerca.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                acerca.iconbitmap(self.icon_path)
        except:
            pass
        
        x = (self.ancho_pantalla - 400) // 2
        y = (self.alto_pantalla - 500) // 2
        acerca.geometry(f"400x500+{x}+{y}")
        
        tk.Label(acerca, text="🐱 ANKUSH CAT 🐱", bg='#1e1e2e', fg='#89b4fa', 
                 font=('Arial', 18, 'bold')).pack(pady=20)
        
        tk.Label(acerca, text="Mascota Virtual de Escritorio", bg='#1e1e2e', fg='#cdd6f4',
                 font=('Arial', 11)).pack(pady=5)
        
        tk.Label(acerca, text="Versión 2.0 - Final Edition", bg='#1e1e2e', fg='#a6e3a1',
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        info_frame = tk.Frame(acerca, bg='#313244', relief='solid', bd=1)
        info_frame.pack(pady=20, padx=30, fill='x')
        
        info_text = """\n✨ Características:\n\n• Mascota interactiva con IA\n• Múltiples modos de juego\n• Sistema de niveles y logros\n• Efectos visuales y sonoros\n• Minijuegos integrados\n• Modo experimental hardcore\n\n🎮 Controles:\n\n• Clic izquierdo: Interactuar\n• Clic derecho: Menú contextual\n• Panel de control: Configuración\n\n💡 Consejo:\n\nExplora todas las pestañas del panel\nde control para descubrir todas las\nfuncionalidades!\n"""
        
        tk.Label(info_frame, text=info_text, bg='#313244', fg='#cdd6f4',
                 font=('Arial', 9), justify='left').pack(pady=15, padx=15)
        
        tk.Label(acerca, text="Creado por Fenix", bg='#1e1e2e', fg='#a78bfa',
                 font=('Arial', 10, 'italic')).pack(pady=10)
        
        tk.Button(acerca, text="Cerrar", command=acerca.destroy, bg='#89b4fa', fg='#1e1e2e',
                 font=('Arial', 10, 'bold'), width=15, relief='flat', cursor='hand2').pack(pady=10)
    
    def mostrar_tutorial(self):
        """Muestra un tutorial rápido al iniciar por primera vez"""
        if os.path.exists('tutorial_visto.flag'):
            return
        
        tutorial = tk.Toplevel(self.root)
        tutorial.title("Tutorial Rápido")
        tutorial.geometry("500x600")
        tutorial.configure(bg='#1e1e2e')
        tutorial.resizable(False, False)
        tutorial.attributes('-topmost', True)
        tutorial.transient(self.root)  # Hacer que sea hija de root
        tutorial.grab_set()  # Bloquear interacción con otras ventanas
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                tutorial.iconbitmap(self.icon_path)
        except:
            pass
        
        x = (self.ancho_pantalla - 500) // 2
        y = (self.alto_pantalla - 600) // 2
        tutorial.geometry(f"500x600+{x}+{y}")
        
        tk.Label(tutorial, text="👋 ¡Bienvenido a Ankush Cat!", bg='#1e1e2e', fg='#89b4fa',
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        canvas = tk.Canvas(tutorial, bg='#1e1e2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(tutorial, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        pasos = [
            ("🖱️ Paso 1: Interactúa", "Haz clic en la mascota para que te hable.\nCada clic aumenta su felicidad!"),
            ("🎮 Paso 2: Panel de Control", "Usa el panel de control para cambiar\nvelocidad, tamaño, efectos y más."),
            ("🎯 Paso 3: Pestañas", "Explora las 6 pestañas:\n• Principal: Controles básicos\n• Efectos: Visuales y sonidos\n• Eventos: Modos especiales\n• Acciones: Configuración\n• Stats: Estadísticas\n• Juegos: Minijuegos y diversión"),
            ("🏆 Paso 4: Juegos", "Juega minijuegos para ganar XP,\nsubir de nivel y desbloquear logros!"),
            ("⚠️ Paso 5: Modo Experimental", "Si te atreves, prueba el modo\nexperimental... pero ten cuidado!"),
            ("💾 Paso 6: Guardar", "Guarda tu configuración en la pestaña\n'Acciones' para no perder tus ajustes.")
        ]
        
        for titulo, desc in pasos:
            frame = tk.Frame(scrollable_frame, bg='#313244', relief='solid', bd=1)
            frame.pack(pady=10, padx=20, fill='x')
            tk.Label(frame, text=titulo, bg='#313244', fg='#a6e3a1',
                    font=('Arial', 11, 'bold')).pack(pady=5, anchor='w', padx=10)
            tk.Label(frame, text=desc, bg='#313244', fg='#cdd6f4',
                    font=('Arial', 9), justify='left').pack(pady=5, anchor='w', padx=10)
        
        def cerrar_tutorial():
            with open('tutorial_visto.flag', 'w') as f:
                f.write('1')
            tutorial.grab_release()  # Liberar el grab
            tutorial.destroy()
        
        # Manejar cierre con X
        tutorial.protocol("WM_DELETE_WINDOW", cerrar_tutorial)
        
        btn_frame = tk.Frame(tutorial, bg='#1e1e2e')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="¡Entendido!", command=cerrar_tutorial, bg='#a6e3a1', fg='#1e1e2e',
                 font=('Arial', 11, 'bold'), width=15, relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="No mostrar de nuevo", command=cerrar_tutorial, bg='#313244', fg='#cdd6f4',
                 font=('Arial', 9), width=20, relief='flat', cursor='hand2').pack(side='left', padx=5)
    
    def juego_memoria(self):
        """Juego de memoria con cartas"""
        self.activo = False
        
        juego = tk.Toplevel(self.root)
        juego.title("🧠 Juego de Memoria")
        juego.geometry("500x550")
        juego.configure(bg='#1e1e2e')
        juego.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                juego.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(juego, text="🧠 JUEGO DE MEMORIA", bg='#1e1e2e', fg='#89b4fa',
                 font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(juego, text="Encuentra las parejas!", bg='#1e1e2e', fg='#cdd6f4',
                 font=('Arial', 10)).pack(pady=5)
        
        simbolos = ['🐱', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
        cartas = simbolos * 2
        random.shuffle(cartas)
        
        estado_juego = {
            'primera': None,
            'segunda': None,
            'parejas_encontradas': 0,
            'intentos': 0,
            'botones': []
        }
        
        def voltear_carta(idx, boton):
            if estado_juego['segunda'] is not None:
                return
            if boton['text'] != '?':
                return
            
            boton.config(text=cartas[idx], bg='#a6e3a1')
            
            if estado_juego['primera'] is None:
                estado_juego['primera'] = (idx, boton)
            else:
                estado_juego['segunda'] = (idx, boton)
                estado_juego['intentos'] += 1
                juego.after(1000, verificar_pareja)
        
        def verificar_pareja():
            idx1, btn1 = estado_juego['primera']
            idx2, btn2 = estado_juego['segunda']
            
            if cartas[idx1] == cartas[idx2]:
                btn1.config(state='disabled', bg='#89b4fa')
                btn2.config(state='disabled', bg='#89b4fa')
                estado_juego['parejas_encontradas'] += 1
                
                if estado_juego['parejas_encontradas'] == 8:
                    messagebox.showinfo("¡Ganaste!", f"¡Completaste el juego en {estado_juego['intentos']} intentos!\n\n+30 XP")
                    self.ganar_experiencia(30)
                    juego.destroy()
                    self.activo = True
            else:
                btn1.config(text='?', bg='#313244')
                btn2.config(text='?', bg='#313244')
            
            estado_juego['primera'] = None
            estado_juego['segunda'] = None
        
        grid_frame = tk.Frame(juego, bg='#1e1e2e')
        grid_frame.pack(pady=20)
        
        for i in range(16):
            fila = i // 4
            col = i % 4
            btn = tk.Button(grid_frame, text='?', width=8, height=4, bg='#313244', fg='#cdd6f4',
                           font=('Arial', 16, 'bold'), relief='raised', bd=3,
                           command=lambda idx=i: voltear_carta(idx, estado_juego['botones'][idx]))
            btn.grid(row=fila, column=col, padx=5, pady=5)
            estado_juego['botones'].append(btn)
        
        tk.Button(juego, text="Cerrar", command=lambda: [juego.destroy(), setattr(self, 'activo', True)],
                 bg='#f38ba8', fg='#1e1e2e', font=('Arial', 10, 'bold'), width=15).pack(pady=10)
    
    def juego_reaccion(self):
        """Juego de tiempo de reacción"""
        self.activo = False
        
        juego = tk.Toplevel(self.root)
        juego.title("⚡ Test de Reacción")
        juego.geometry("400x400")
        juego.configure(bg='#1e1e2e')
        juego.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                juego.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(juego, text="⚡ TEST DE REACCIÓN", bg='#1e1e2e', fg='#89b4fa',
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        instrucciones = tk.Label(juego, text="Haz clic cuando el círculo se ponga VERDE", 
                                bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 11))
        instrucciones.pack(pady=10)
        
        canvas = tk.Canvas(juego, width=200, height=200, bg='#313244', highlightthickness=0)
        canvas.pack(pady=20)
        
        circulo = canvas.create_oval(50, 50, 150, 150, fill='#f38ba8', outline='')
        
        estado = {'esperando': False, 'tiempo_inicio': 0, 'intentos': 0, 'tiempos': []}
        
        def iniciar_test():
            estado['esperando'] = False
            canvas.itemconfig(circulo, fill='#f38ba8')
            instrucciones.config(text="Espera...")
            tiempo_espera = random.randint(1000, 4000)
            juego.after(tiempo_espera, mostrar_verde)
        
        def mostrar_verde():
            canvas.itemconfig(circulo, fill='#a6e3a1')
            instrucciones.config(text="¡AHORA! Haz clic!")
            estado['esperando'] = True
            estado['tiempo_inicio'] = time.time()
        
        def click_circulo(event):
            if not estado['esperando']:
                instrucciones.config(text="¡Demasiado pronto! Espera al verde")
                return
            
            tiempo_reaccion = (time.time() - estado['tiempo_inicio']) * 1000
            estado['tiempos'].append(tiempo_reaccion)
            estado['intentos'] += 1
            
            instrucciones.config(text=f"Tiempo: {tiempo_reaccion:.0f}ms")
            
            if estado['intentos'] < 3:
                juego.after(1500, iniciar_test)
            else:
                promedio = sum(estado['tiempos']) / len(estado['tiempos'])
                messagebox.showinfo("Resultado", f"Promedio: {promedio:.0f}ms\n\n+20 XP")
                self.ganar_experiencia(20)
                juego.destroy()
                self.activo = True
        
        canvas.bind('<Button-1>', click_circulo)
        
        tk.Button(juego, text="Iniciar", command=iniciar_test, bg='#a6e3a1', fg='#1e1e2e',
                 font=('Arial', 11, 'bold'), width=15).pack(pady=10)
    
    def juego_esquivar(self):
        """Juego de esquivar obstáculos"""
        self.activo = False
        
        juego = tk.Toplevel(self.root)
        juego.title("🎯 Esquiva los Obstáculos")
        juego.geometry("400x500")
        juego.configure(bg='#1e1e2e')
        juego.attributes('-topmost', True)
        
        # Aplicar icono
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                juego.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(juego, text="🎯 ESQUIVA LOS OBSTÁCULOS", bg='#1e1e2e', fg='#89b4fa',
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        canvas = tk.Canvas(juego, width=350, height=400, bg='#313244', highlightthickness=0)
        canvas.pack(pady=10)
        
        jugador = canvas.create_oval(160, 350, 190, 380, fill='#89b4fa')
        jugador_x = [175]
        
        obstaculos = []
        puntos = [0]
        juego_activo = [True]
        
        def mover_jugador(event):
            if event.keysym == 'Left' and jugador_x[0] > 15:
                jugador_x[0] -= 20
            elif event.keysym == 'Right' and jugador_x[0] < 335:
                jugador_x[0] += 20
            canvas.coords(jugador, jugador_x[0]-15, 350, jugador_x[0]+15, 380)
        
        juego.bind('<Left>', mover_jugador)
        juego.bind('<Right>', mover_jugador)
        juego.focus_set()
        
        def crear_obstaculo():
            if not juego_activo[0]:
                return
            x = random.randint(15, 335)
            obs = canvas.create_rectangle(x-15, 0, x+15, 30, fill='#f38ba8')
            obstaculos.append({'obj': obs, 'y': 0})
            juego.after(1500, crear_obstaculo)
        
        def actualizar():
            if not juego_activo[0]:
                return
            
            for obs in obstaculos[:]:
                obs['y'] += 5
                canvas.coords(obs['obj'], 
                             canvas.coords(obs['obj'])[0], obs['y'],
                             canvas.coords(obs['obj'])[2], obs['y']+30)
                
                obs_coords = canvas.coords(obs['obj'])
                jug_coords = canvas.coords(jugador)
                
                if (obs_coords[3] >= jug_coords[1] and obs_coords[1] <= jug_coords[3] and
                    obs_coords[2] >= jug_coords[0] and obs_coords[0] <= jug_coords[2]):
                    juego_activo[0] = False
                    messagebox.showinfo("Game Over", f"Puntos: {puntos[0]}\n\n+{puntos[0]//10} XP")
                    self.ganar_experiencia(puntos[0]//10)
                    juego.destroy()
                    self.activo = True
                    return
                
                if obs['y'] > 400:
                    canvas.delete(obs['obj'])
                    obstaculos.remove(obs)
                    puntos[0] += 1
            
            juego.after(50, actualizar)
        
        crear_obstaculo()
        actualizar()
    
    def reproducir_video_intro(self):
        """Reproduce un video aleatorio de la carpeta assets/video al inicio"""
        carpeta_videos = os.path.join("assets", "video")
        
        # Verificar si existe la carpeta
        if not os.path.exists(carpeta_videos):
            return
        
        # Buscar videos en la carpeta
        extensiones_video = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        videos = [f for f in os.listdir(carpeta_videos) if os.path.splitext(f)[1].lower() in extensiones_video]
        
        if not videos:
            return
        
        # Seleccionar video aleatorio
        video_seleccionado = random.choice(videos)
        video_path = os.path.abspath(os.path.join(carpeta_videos, video_seleccionado))
        
        # Intentar reproducir con VLC primero, luego con reproductor predeterminado
        try:
            # Buscar VLC en ubicaciones comunes
            vlc_paths = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\VideoLAN\VLC\vlc.exe")
            ]
            
            vlc_encontrado = False
            for vlc_path in vlc_paths:
                if os.path.exists(vlc_path):
                    subprocess.Popen([vlc_path, video_path])
                    vlc_encontrado = True
                    break
            
            # Si no se encontró VLC, intentar con reproductor predeterminado
            if not vlc_encontrado:
                if sys.platform.startswith('win'):
                    os.startfile(video_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', video_path])
                else:
                    subprocess.call(['xdg-open', video_path])
        except Exception as e:
            # Si falla, mostrar mensaje informativo
            messagebox.showwarning(
                "Video no disponible",
                f"No se pudo reproducir el video de intro.\n\nPara ver los videos, instala VLC Media Player desde:\nhttps://www.videolan.org/vlc/\n\nO asocia un reproductor de video en Windows."
            )

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.withdraw()
        app = ImagenFlotante(root)
        root.mainloop()
    except Exception as e:
        import traceback
        with open('error_log.txt', 'w', encoding='utf-8') as f:
            f.write(f"Error: {e}\n\n")
            f.write(traceback.format_exc())
        print(f"ERROR: {e}")
        print("\nDetalles guardados en error_log.txt")
        input("Presiona Enter para cerrar...")

    def eliminar_clones(self):
        """Elimina todos los clones creados"""
        if not self.clones:
            messagebox.showinfo("Sin Clones", "No hay clones para eliminar")
            return
        
        respuesta = messagebox.askyesno("Eliminar Clones", f"¿Eliminar todos los {len(self.clones)} clones?")
        if respuesta:
            for clon in self.clones:
                try:
                    clon['ventana'].destroy()
                except:
                    pass
            self.clones = []
            self.mostrar_texto("Todos los clones eliminados!")
    
    def cambiar_volumen(self):
        """Abre ventana para ajustar volumen"""
        vol_win = tk.Toplevel(self.root)
        vol_win.title("Ajustar Volumen")
        vol_win.geometry("300x150")
        vol_win.configure(bg='#1e1e2e')
        vol_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                vol_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(vol_win, text="🔊 Volumen", bg='#1e1e2e', fg='#89b4fa', font=('Arial', 12, 'bold')).pack(pady=10)
        
        def cambiar_vol(val):
            volumen = int(val) / 100
            mixer.music.set_volume(volumen)
        
        slider = tk.Scale(vol_win, from_=0, to=100, orient="horizontal", command=cambiar_vol,
                         bg='#312e81', fg='#e0e7ff', troughcolor='#4c1d95', highlightthickness=0,
                         activebackground='#8b5cf6', relief='flat', font=('Arial', 9, 'bold'),
                         sliderrelief='flat', bd=0, length=250)
        slider.set(50)
        slider.pack(pady=20)
    
    def captura_manual(self):
        """Toma una captura de pantalla manualmente"""
        try:
            from PIL import ImageGrab
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            screenshot = ImageGrab.grab()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/screenshot_{timestamp}.png"
            screenshot.save(filename)
            messagebox.showinfo("Captura", f"Captura guardada:\n{filename}")
            self.mostrar_texto("📸 Captura guardada!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo tomar captura: {e}")
    
    def cambiar_opacidad_ventana(self):
        """Cambia la opacidad de la ventana de control"""
        opacidad = simpledialog.askfloat("Opacidad", "Opacidad de ventana de control (0.1 - 1.0):", 
                                         minvalue=0.1, maxvalue=1.0, initialvalue=1.0)
        if opacidad:
            self.root.attributes('-alpha', opacidad)
    
    def cambiar_color_borde(self):
        """Cambia el color del borde de la ventana"""
        color = colorchooser.askcolor(title="Color del borde")
        if color[1]:
            self.root.configure(bg=color[1])
            self.mostrar_texto(f"Borde cambiado a {color[1]}")
    
    def resetear_velocidad(self):
        """Resetea la velocidad a valores normales"""
        self.vel_x = 3 if self.vel_x > 0 else -3
        self.vel_y = 3 if self.vel_y > 0 else -3
        messagebox.showinfo("Velocidad", "Velocidad reseteada a 3")
        self.mostrar_texto("Velocidad normal!")
    
    def centrar_pantalla(self):
        """Centra la mascota en la pantalla"""
        self.x = self.ancho_pantalla // 2 - self.tamano // 2
        self.y = self.alto_pantalla // 2 - self.tamano // 2
        self.mostrar_texto("Centrado!")
    
    def exportar_stats(self):
        """Exporta las estadísticas a un archivo de texto"""
        try:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            horas = tiempo_transcurrido // 3600
            minutos = (tiempo_transcurrido % 3600) // 60
            segundos = tiempo_transcurrido % 60
            
            stats_text = f"""
=== ESTADÍSTICAS DE ANKUSH CAT ===
Fecha: {time.strftime("%Y-%m-%d %H:%M:%S")}

Usuario: {self.username}
Nivel: {self.nivel}
Experiencia: {self.experiencia}/100
Estado de ánimo: {self.estado_animo}

Tiempo de ejecución: {horas}h {minutos}m {segundos}s
Total de clicks: {self.click_contador}
Distancia recorrida: {int(self.distancia_recorrida)} px

Hambre: {int(self.hambre)}%
Felicidad: {int(self.felicidad)}%

Clones activos: {len(self.clones)}
Logros desbloqueados: {len(self.logros)}
Items en inventario: {len(self.inventario)}

=== LOGROS ===
{chr(10).join(['- ' + logro for logro in self.logros]) if self.logros else 'Ninguno'}

=== INVENTARIO ===
{chr(10).join(['- ' + item for item in self.inventario]) if self.inventario else 'Vacío'}
"""
            
            filename = f"stats_ankush_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(stats_text)
            
            messagebox.showinfo("Exportado", f"Estadísticas exportadas a:\n{filename}")
            self.mostrar_texto("📊 Stats exportadas!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def juego_memoria(self):
        """Juego de memoria con cartas"""
        memoria_win = tk.Toplevel(self.root)
        memoria_win.title("🧠 Juego de Memoria")
        memoria_win.geometry("500x600")
        memoria_win.configure(bg='#1e1e2e')
        memoria_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                memoria_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(memoria_win, text="🧠 Juego de Memoria", bg='#1e1e2e', fg='#89b4fa', 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Crear tablero 4x4
        emojis = ['🐱', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
        cartas = emojis * 2
        random.shuffle(cartas)
        
        estado = {
            'primera': None,
            'segunda': None,
            'bloqueado': False,
            'pares': 0,
            'intentos': 0
        }
        
        intentos_label = tk.Label(memoria_win, text="Intentos: 0", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 11))
        intentos_label.pack(pady=5)
        
        frame_tablero = tk.Frame(memoria_win, bg='#1e1e2e')
        frame_tablero.pack(pady=20)
        
        botones = []
        
        def click_carta(idx):
            if estado['bloqueado'] or botones[idx]['text'] != '❓':
                return
            
            botones[idx].config(text=cartas[idx], bg='#89b4fa')
            
            if estado['primera'] is None:
                estado['primera'] = idx
            elif estado['segunda'] is None:
                estado['segunda'] = idx
                estado['intentos'] += 1
                intentos_label.config(text=f"Intentos: {estado['intentos']}")
                estado['bloqueado'] = True
                memoria_win.after(1000, verificar_par)
        
        def verificar_par():
            idx1 = estado['primera']
            idx2 = estado['segunda']
            
            if cartas[idx1] == cartas[idx2]:
                estado['pares'] += 1
                if estado['pares'] == 8:
                    messagebox.showinfo("¡Ganaste!", f"Completaste el juego en {estado['intentos']} intentos!")
                    self.ganar_experiencia(30)
                    self.agregar_item("Trofeo Memoria")
                    memoria_win.destroy()
            else:
                botones[idx1].config(text='❓', bg='#313244')
                botones[idx2].config(text='❓', bg='#313244')
            
            estado['primera'] = None
            estado['segunda'] = None
            estado['bloqueado'] = False
        
        for i in range(16):
            btn = tk.Button(frame_tablero, text='❓', font=('Arial', 20), width=4, height=2,
                          bg='#313244', fg='#cdd6f4', command=lambda idx=i: click_carta(idx))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)
            botones.append(btn)
    
    def juego_reaccion(self):
        """Test de tiempo de reacción"""
        reaccion_win = tk.Toplevel(self.root)
        reaccion_win.title("⚡ Test de Reacción")
        reaccion_win.geometry("400x300")
        reaccion_win.configure(bg='#1e1e2e')
        reaccion_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                reaccion_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(reaccion_win, text="⚡ Test de Reacción", bg='#1e1e2e', fg='#89b4fa',
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        instrucciones = tk.Label(reaccion_win, text="Haz clic cuando el círculo se ponga verde", 
                                bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 10))
        instrucciones.pack(pady=10)
        
        canvas = tk.Canvas(reaccion_win, width=200, height=200, bg='#313244', highlightthickness=0)
        canvas.pack(pady=20)
        
        circulo = canvas.create_oval(50, 50, 150, 150, fill='#f38ba8')
        
        estado = {'esperando': False, 'tiempo_inicio': 0}
        
        def iniciar_test():
            canvas.itemconfig(circulo, fill='#f38ba8')
            estado['esperando'] = False
            tiempo_espera = random.randint(2000, 5000)
            reaccion_win.after(tiempo_espera, mostrar_verde)
        
        def mostrar_verde():
            canvas.itemconfig(circulo, fill='#a6e3a1')
            estado['esperando'] = True
            estado['tiempo_inicio'] = time.time()
        
        def click_circulo(event):
            if estado['esperando']:
                tiempo_reaccion = (time.time() - estado['tiempo_inicio']) * 1000
                messagebox.showinfo("Resultado", f"Tu tiempo de reacción: {tiempo_reaccion:.0f} ms")
                if tiempo_reaccion < 300:
                    self.ganar_experiencia(20)
                    self.mostrar_texto("¡Reacción increíble!")
                reaccion_win.destroy()
            elif not estado['esperando'] and canvas.itemcget(circulo, 'fill') == '#f38ba8':
                messagebox.showwarning("Muy pronto", "¡Esperaste muy poco! Inténtalo de nuevo.")
                iniciar_test()
        
        canvas.bind('<Button-1>', click_circulo)
        iniciar_test()
    
    def juego_esquivar(self):
        """Juego de esquivar obstáculos"""
        esquivar_win = tk.Toplevel(self.root)
        esquivar_win.title("🎯 Esquiva Obstáculos")
        esquivar_win.geometry("600x400")
        esquivar_win.configure(bg='#1e1e2e')
        esquivar_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                esquivar_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(esquivar_win, text="🎯 Esquiva Obstáculos", bg='#1e1e2e', fg='#89b4fa',
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        canvas = tk.Canvas(esquivar_win, width=580, height=350, bg='#313244', highlightthickness=0)
        canvas.pack(pady=10)
        
        # Jugador
        jugador_x = 290
        jugador_y = 300
        jugador = canvas.create_rectangle(jugador_x-15, jugador_y-15, jugador_x+15, jugador_y+15, fill='#89b4fa')
        
        # Obstáculos
        obstaculos = []
        puntos = [0]
        juego_activo = [True]
        
        puntos_label = tk.Label(esquivar_win, text="Puntos: 0", bg='#1e1e2e', fg='#a6e3a1', font=('Arial', 11, 'bold'))
        puntos_label.pack()
        
        def mover_jugador(event):
            nonlocal jugador_x
            if event.keysym == 'Left' and jugador_x > 20:
                jugador_x -= 20
            elif event.keysym == 'Right' and jugador_x < 560:
                jugador_x += 20
            canvas.coords(jugador, jugador_x-15, jugador_y-15, jugador_x+15, jugador_y+15)
        
        def crear_obstaculo():
            if not juego_activo[0]:
                return
            x = random.randint(20, 560)
            obst = canvas.create_rectangle(x-15, 0, x+15, 30, fill='#f38ba8')
            obstaculos.append({'obj': obst, 'y': 0})
            esquivar_win.after(1000, crear_obstaculo)
        
        def actualizar_juego():
            if not juego_activo[0]:
                return
            
            for obst in obstaculos[:]:
                obst['y'] += 5
                coords = canvas.coords(obst['obj'])
                canvas.coords(obst['obj'], coords[0], obst['y'], coords[2], obst['y']+30)
                
                # Verificar colisión
                if abs(coords[0]+15 - jugador_x) < 30 and abs(obst['y']+15 - jugador_y) < 30:
                    juego_activo[0] = False
                    messagebox.showinfo("Game Over", f"Puntos finales: {puntos[0]}")
                    if puntos[0] > 20:
                        self.ganar_experiencia(25)
                        self.agregar_item("Trofeo Esquivador")
                    esquivar_win.destroy()
                    return
                
                # Eliminar si sale de pantalla
                if obst['y'] > 350:
                    canvas.delete(obst['obj'])
                    obstaculos.remove(obst)
                    puntos[0] += 1
                    puntos_label.config(text=f"Puntos: {puntos[0]}")
            
            esquivar_win.after(50, actualizar_juego)
        
        esquivar_win.bind('<Left>', mover_jugador)
        esquivar_win.bind('<Right>', mover_jugador)
        esquivar_win.focus_set()
        
        crear_obstaculo()
        actualizar_juego()
    
    def reproducir_video_intro(self):
        """Reproduce video de introducción si existe"""
        try:
            video_path = os.path.join("assets", "video", "intro.mp4")
            if os.path.exists(video_path):
                import subprocess
                subprocess.Popen(['start', video_path], shell=True)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    mostrar_splash_actualizacion(root)
    app = ImagenFlotante(root)
    root.mainloop()

    def crear_pagina_mods(self):
        """Página para gestionar mods"""
        style_bg = '#0a0e27'
        style_fg = '#e0e7ff'
        style_card = '#1e1b4b'
        
        self.pagina_mods = tk.Frame(self.contenedor, bg=style_bg)
        
        tk.Label(self.pagina_mods, text="🎮 Sistema de Mods", bg=style_bg, fg='#6366f1', font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Botones de control
        btn_frame = tk.Frame(self.pagina_mods, bg=style_bg)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Recargar Mods", command=self.recargar_mods, bg='#89b4fa', fg='#1e1e2e', 
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📂 Abrir Carpeta", command=self.abrir_carpeta_mods, bg='#a6e3a1', fg='#1e1e2e',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="❓ Ayuda", command=self.ayuda_mods, bg='#f9e2af', fg='#1e1e2e',
                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.pagina_mods, bg=style_bg, highlightthickness=0, width=400)
        scrollbar = tk.Scrollbar(self.pagina_mods, orient="vertical", command=canvas.yview)
        self.mods_scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        self.mods_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.mods_scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.actualizar_lista_mods()
    
    def cargar_mods(self):
        """Carga todos los mods de la carpeta mods/"""
        import importlib.util
        
        mods_dir = "mods"
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
            return
        
        for archivo in os.listdir(mods_dir):
            if archivo.endswith('.py') and not archivo.startswith('_'):
                try:
                    mod_path = os.path.join(mods_dir, archivo)
                    spec = importlib.util.spec_from_file_location(archivo[:-3], mod_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    if hasattr(mod, 'MOD_INFO') and hasattr(mod, 'inicializar'):
                        self.mods_cargados.append({
                            'nombre': archivo[:-3],
                            'info': mod.MOD_INFO,
                            'modulo': mod,
                            'activo': False
                        })
                        print(f"✅ Mod encontrado: {mod.MOD_INFO['nombre']}")
                except Exception as e:
                    print(f"❌ Error cargando mod {archivo}: {e}")
    
    def activar_mod(self, nombre_mod):
        """Activa un mod específico"""
        for mod in self.mods_cargados:
            if mod['nombre'] == nombre_mod:
                try:
                    mod['modulo'].inicializar(self)
                    mod['activo'] = True
                    self.mods_activos[nombre_mod] = mod['modulo']
                    self.mostrar_texto(f"✅ {mod['info']['nombre']} activado!")
                    self.actualizar_lista_mods()
                except Exception as e:
                    messagebox.showerror("Error", f"Error activando mod:\n{e}")
                break
    
    def desactivar_mod(self, nombre_mod):
        """Desactiva un mod específico"""
        for mod in self.mods_cargados:
            if mod['nombre'] == nombre_mod and mod['activo']:
                try:
                    if hasattr(mod['modulo'], 'finalizar'):
                        mod['modulo'].finalizar(self)
                    mod['activo'] = False
                    if nombre_mod in self.mods_activos:
                        del self.mods_activos[nombre_mod]
                    self.mostrar_texto(f"❌ {mod['info']['nombre']} desactivado!")
                    self.actualizar_lista_mods()
                except Exception as e:
                    messagebox.showerror("Error", f"Error desactivando mod:\n{e}")
                break
    
    def actualizar_lista_mods(self):
        """Actualiza la lista visual de mods"""
        for widget in self.mods_scrollable_frame.winfo_children():
            widget.destroy()
        
        style_bg = '#0a0e27'
        style_card = '#1e1b4b'
        
        if not self.mods_cargados:
            tk.Label(self.mods_scrollable_frame, text="No hay mods instalados\n\nColoca archivos .py en la carpeta 'mods/'",
                    bg=style_bg, fg='#a5b4fc', font=('Arial', 10), justify='center').pack(pady=50)
            return
        
        for mod in self.mods_cargados:
            mod_frame = tk.Frame(self.mods_scrollable_frame, bg=style_card, relief='flat', bd=0)
            mod_frame.pack(pady=8, padx=20, fill='x')
            
            color_borde = '#a6e3a1' if mod['activo'] else '#6366f1'
            tk.Frame(mod_frame, bg=color_borde, height=3).pack(fill='x')
            
            content = tk.Frame(mod_frame, bg=style_card)
            content.pack(pady=10, padx=15, fill='x')
            
            # Título y estado
            header = tk.Frame(content, bg=style_card)
            header.pack(fill='x')
            
            estado_emoji = "✅" if mod['activo'] else "⭕"
            tk.Label(header, text=f"{estado_emoji} {mod['info']['nombre']}", bg=style_card, fg='#e0e7ff',
                    font=('Arial', 11, 'bold')).pack(side='left')
            
            tk.Label(header, text=f"v{mod['info']['version']}", bg=style_card, fg='#a5b4fc',
                    font=('Arial', 8)).pack(side='left', padx=5)
            
            # Descripción
            tk.Label(content, text=mod['info']['descripcion'], bg=style_card, fg='#a5b4fc',
                    font=('Arial', 9), wraplength=300, justify='left').pack(anchor='w', pady=3)
            
            # Autor
            tk.Label(content, text=f"👤 {mod['info']['autor']}", bg=style_card, fg='#6c7086',
                    font=('Arial', 8)).pack(anchor='w')
            
            # Configuraciones del mod (si tiene)
            if mod['activo'] and hasattr(mod['modulo'], 'MOD_CONFIG'):
                config_frame = tk.Frame(content, bg='#313244', relief='solid', bd=1)
                config_frame.pack(fill='x', pady=8)
                
                tk.Label(config_frame, text="⚙️ Configuración", bg='#313244', fg='#89b4fa',
                        font=('Arial', 9, 'bold')).pack(pady=5)
                
                for key, cfg in mod['modulo'].MOD_CONFIG.items():
                    self.crear_control_config(config_frame, mod, key, cfg)
            
            # Botón toggle
            btn_frame = tk.Frame(content, bg=style_card)
            btn_frame.pack(pady=5)
            
            if mod['activo']:
                tk.Button(btn_frame, text="Desactivar", 
                         command=lambda n=mod['nombre']: self.desactivar_mod(n),
                         bg='#f38ba8', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                         relief='flat', cursor='hand2', width=12).pack(side='left', padx=3)
                
                if hasattr(mod['modulo'], 'MOD_CONFIG'):
                    tk.Button(btn_frame, text="⚙️ Configurar",
                             command=lambda m=mod: self.abrir_config_mod(m),
                             bg='#89b4fa', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                             relief='flat', cursor='hand2', width=12).pack(side='left', padx=3)
            else:
                tk.Button(btn_frame, text="Activar",
                         command=lambda n=mod['nombre']: self.activar_mod(n),
                         bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                         relief='flat', cursor='hand2', width=12).pack()
    
    def recargar_mods(self):
        """Recarga todos los mods"""
        # Desactivar mods activos
        for nombre_mod in list(self.mods_activos.keys()):
            self.desactivar_mod(nombre_mod)
        
        # Limpiar lista
        self.mods_cargados = []
        self.mods_activos = {}
        
        # Recargar
        self.cargar_mods()
        self.actualizar_lista_mods()
        messagebox.showinfo("Mods", f"Mods recargados!\n\nEncontrados: {len(self.mods_cargados)}")
    
    def abrir_carpeta_mods(self):
        """Abre la carpeta de mods en el explorador"""
        mods_dir = os.path.abspath("mods")
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
        os.startfile(mods_dir)
    
    def ayuda_mods(self):
        """Muestra ayuda sobre el sistema de mods"""
        ayuda_win = tk.Toplevel(self.root)
        ayuda_win.title("Ayuda - Sistema de Mods")
        ayuda_win.geometry("500x600")
        ayuda_win.configure(bg='#1e1e2e')
        ayuda_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                ayuda_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(ayuda_win, text="🎮 Sistema de Mods", bg='#1e1e2e', fg='#89b4fa',
                font=('Arial', 14, 'bold')).pack(pady=15)
        
        canvas = tk.Canvas(ayuda_win, bg='#1e1e2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(ayuda_win, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg='#1e1e2e')
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        texto = """
📁 ESTRUCTURA DE UN MOD

Crea un archivo .py en la carpeta 'mods/' con:

MOD_INFO = {
    "nombre": "Mi Mod",
    "version": "1.0",
    "autor": "Tu Nombre",
    "descripcion": "Descripcion"
}

def inicializar(mascota):
    # Codigo al activar
    mascota.frases.append("Hola!")
    print("Mod cargado!")

✨ FUNCIONES OPCIONALES

def actualizar(mascota):
    # Se ejecuta cada frame
    pass

def on_click(mascota, event):
    # Al hacer clic en mascota
    pass

def finalizar(mascota):
    # Al desactivar mod
    pass

💡 EJEMPLOS

# Cambiar velocidad
def inicializar(mascota):
    mascota.vel_x = 20
    mascota.vel_y = 20

# Crear clones automaticos
import time
ultimo = [0]

def actualizar(mascota):
    if time.time() - ultimo[0] > 5:
        mascota.crear_clon_automatico()
        ultimo[0] = time.time()

# Nuevo modo personalizado
def inicializar(mascota):
    mascota.modo_custom = True

def actualizar(mascota):
    if mascota.modo_custom:
        # Tu logica aqui
        pass

🎯 ACCESO A LA MASCOTA

Puedes modificar:
- mascota.vel_x, vel_y (velocidad)
- mascota.tamano (tamaño)
- mascota.frases (lista de frases)
- mascota.x, mascota.y (posicion)
- Cualquier variable o funcion!

⚠️ ADVERTENCIAS

- Los mods tienen acceso total
- Un mod mal hecho puede crashear
- Guarda antes de probar mods nuevos
- Lee el codigo antes de activar

🚀 COMO USAR

1. Crea archivo .py en mods/
2. Sigue la estructura
3. Haz clic en "Recargar Mods"
4. Activa tu mod
5. Disfruta!
"""
        
        tk.Label(frame, text=texto, bg='#1e1e2e', fg='#cdd6f4',
                font=('Consolas', 9), justify='left').pack(pady=10, padx=10)
        
        tk.Button(ayuda_win, text="Cerrar", command=ayuda_win.destroy,
                 bg='#89b4fa', fg='#1e1e2e', font=('Arial', 10, 'bold'),
                 relief='flat', cursor='hand2', width=15).pack(pady=10)
    
    def ejecutar_mods_actualizar(self):
        """Ejecuta la función actualizar() de todos los mods activos"""
        for nombre_mod, mod in self.mods_activos.items():
            if hasattr(mod, 'actualizar'):
                try:
                    mod.actualizar(self)
                except Exception as e:
                    print(f"Error en mod {nombre_mod}.actualizar(): {e}")
    
    def ejecutar_mods_click(self, event):
        """Ejecuta la función on_click() de todos los mods activos"""
        for nombre_mod, mod in self.mods_activos.items():
            if hasattr(mod, 'on_click'):
                try:
                    mod.on_click(self, event)
                except Exception as e:
                    print(f"Error en mod {nombre_mod}.on_click(): {e}")

    def crear_control_config(self, parent, mod, key, cfg):
        """Crea un control de configuración según el tipo"""
        control_frame = tk.Frame(parent, bg='#313244')
        control_frame.pack(fill='x', padx=10, pady=3)
        
        # Label
        tk.Label(control_frame, text=f"{cfg['nombre']}:", bg='#313244', fg='#cdd6f4',
                font=('Arial', 9)).pack(side='left', padx=5)
        
        if cfg['tipo'] == 'slider':
            # Slider
            def on_change(val):
                if hasattr(mod['modulo'], 'on_config_change'):
                    mod['modulo'].on_config_change(self, key, int(float(val)))
            
            slider = tk.Scale(control_frame, from_=cfg['min'], to=cfg['max'], orient='horizontal',
                            command=on_change, bg='#45475a', fg='#cdd6f4', troughcolor='#1e1e2e',
                            highlightthickness=0, relief='flat', length=150)
            
            # Obtener valor actual
            if hasattr(mod['modulo'], 'config_actual'):
                slider.set(mod['modulo'].config_actual.get(key, cfg['default']))
            else:
                slider.set(cfg['default'])
            
            slider.pack(side='left', padx=5)
        
        elif cfg['tipo'] == 'checkbox':
            # Checkbox
            var = tk.BooleanVar(value=cfg['default'])
            if hasattr(mod['modulo'], 'config_actual'):
                var.set(mod['modulo'].config_actual.get(key, cfg['default']))
            
            def on_toggle():
                if hasattr(mod['modulo'], 'on_config_change'):
                    mod['modulo'].on_config_change(self, key, var.get())
            
            tk.Checkbutton(control_frame, variable=var, command=on_toggle,
                          bg='#313244', fg='#cdd6f4', selectcolor='#45475a',
                          activebackground='#313244').pack(side='left', padx=5)
        
        elif cfg['tipo'] == 'color':
            # Botón de color
            def elegir_color():
                from tkinter import colorchooser
                color = colorchooser.askcolor(title=f"Elegir {cfg['nombre']}")
                if color[1]:
                    if hasattr(mod['modulo'], 'on_config_change'):
                        mod['modulo'].on_config_change(self, key, color[1])
                    btn_color.config(bg=color[1])
            
            color_actual = cfg['default']
            if hasattr(mod['modulo'], 'config_actual'):
                color_actual = mod['modulo'].config_actual.get(key, cfg['default'])
            
            btn_color = tk.Button(control_frame, text="  ", bg=color_actual,
                                 command=elegir_color, width=3, relief='solid', bd=1)
            btn_color.pack(side='left', padx=5)
    
    def abrir_config_mod(self, mod):
        """Abre ventana de configuración avanzada del mod"""
        config_win = tk.Toplevel(self.root)
        config_win.title(f"Configurar {mod['info']['nombre']}")
        config_win.geometry("400x500")
        config_win.configure(bg='#1e1e2e')
        config_win.attributes('-topmost', True)
        
        try:
            if self.icon_path and os.path.exists(self.icon_path):
                config_win.iconbitmap(self.icon_path)
        except:
            pass
        
        tk.Label(config_win, text=f"⚙️ {mod['info']['nombre']}", bg='#1e1e2e', fg='#89b4fa',
                font=('Arial', 14, 'bold')).pack(pady=15)
        
        # Canvas con scroll
        canvas = tk.Canvas(config_win, bg='#1e1e2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(config_win, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg='#1e1e2e')
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        if hasattr(mod['modulo'], 'MOD_CONFIG'):
            for key, cfg in mod['modulo'].MOD_CONFIG.items():
                # Card para cada configuración
                card = tk.Frame(frame, bg='#313244', relief='solid', bd=1)
                card.pack(fill='x', pady=8, padx=10)
                
                tk.Label(card, text=cfg['nombre'], bg='#313244', fg='#89b4fa',
                        font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(card, text=cfg['descripcion'], bg='#313244', fg='#a5b4fc',
                        font=('Arial', 9), wraplength=340).pack(anchor='w', padx=10, pady=3)
                
                control_frame = tk.Frame(card, bg='#313244')
                control_frame.pack(pady=10, padx=10)
                
                if cfg['tipo'] == 'slider':
                    # Slider grande
                    valor_label = tk.Label(control_frame, text="", bg='#313244', fg='#a6e3a1',
                                          font=('Arial', 12, 'bold'))
                    valor_label.pack()
                    
                    def on_change(val, k=key, lbl=valor_label):
                        lbl.config(text=f"{int(float(val))}")
                        if hasattr(mod['modulo'], 'on_config_change'):
                            mod['modulo'].on_config_change(self, k, int(float(val)))
                    
                    slider = tk.Scale(control_frame, from_=cfg['min'], to=cfg['max'], orient='horizontal',
                                    command=on_change, bg='#45475a', fg='#cdd6f4', troughcolor='#1e1e2e',
                                    highlightthickness=0, relief='flat', length=300, width=20)
                    
                    if hasattr(mod['modulo'], 'config_actual'):
                        val = mod['modulo'].config_actual.get(key, cfg['default'])
                        slider.set(val)
                        valor_label.config(text=f"{val}")
                    else:
                        slider.set(cfg['default'])
                        valor_label.config(text=f"{cfg['default']}")
                    
                    slider.pack(pady=5)
                    
                    # Botones rápidos
                    btn_frame = tk.Frame(control_frame, bg='#313244')
                    btn_frame.pack(pady=5)
                    
                    tk.Button(btn_frame, text="Min", command=lambda s=slider, m=cfg['min']: s.set(m),
                             bg='#6c7086', fg='#cdd6f4', font=('Arial', 8), width=6).pack(side='left', padx=2)
                    tk.Button(btn_frame, text="Default", command=lambda s=slider, d=cfg['default']: s.set(d),
                             bg='#89b4fa', fg='#1e1e2e', font=('Arial', 8), width=6).pack(side='left', padx=2)
                    tk.Button(btn_frame, text="Max", command=lambda s=slider, m=cfg['max']: s.set(m),
                             bg='#6c7086', fg='#cdd6f4', font=('Arial', 8), width=6).pack(side='left', padx=2)
                
                elif cfg['tipo'] == 'checkbox':
                    var = tk.BooleanVar(value=cfg['default'])
                    if hasattr(mod['modulo'], 'config_actual'):
                        var.set(mod['modulo'].config_actual.get(key, cfg['default']))
                    
                    def on_toggle(k=key, v=var):
                        if hasattr(mod['modulo'], 'on_config_change'):
                            mod['modulo'].on_config_change(self, k, v.get())
                    
                    tk.Checkbutton(control_frame, text="Activado" if var.get() else "Desactivado",
                                  variable=var, command=on_toggle, bg='#313244', fg='#cdd6f4',
                                  selectcolor='#45475a', activebackground='#313244',
                                  font=('Arial', 10, 'bold')).pack()
                
                elif cfg['tipo'] == 'color':
                    color_actual = cfg['default']
                    if hasattr(mod['modulo'], 'config_actual'):
                        color_actual = mod['modulo'].config_actual.get(key, cfg['default'])
                    
                    color_display = tk.Frame(control_frame, bg=color_actual, width=100, height=50,
                                            relief='solid', bd=2)
                    color_display.pack(pady=5)
                    
                    def elegir_color(k=key, display=color_display):
                        from tkinter import colorchooser
                        color = colorchooser.askcolor(title=f"Elegir {cfg['nombre']}")
                        if color[1]:
                            if hasattr(mod['modulo'], 'on_config_change'):
                                mod['modulo'].on_config_change(self, k, color[1])
                            display.config(bg=color[1])
                    
                    tk.Button(control_frame, text="Cambiar Color", command=elegir_color,
                             bg='#89b4fa', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                             relief='flat', cursor='hand2').pack(pady=5)
        
        tk.Button(config_win, text="Cerrar", command=config_win.destroy,
                 bg='#6c7086', fg='#cdd6f4', font=('Arial', 10, 'bold'),
                 relief='flat', cursor='hand2', width=15).pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Verificar actualizaciones al iniciar
    mostrar_splash_actualizacion(root)
    
    # Iniciar programa normal
    app = ImagenFlotante(root)
    root.mainloop()

