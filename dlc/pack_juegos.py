# DLC: Pack de Juegos
# Añade 5 nuevos minijuegos a Ankush Cat

import tkinter as tk
from tkinter import messagebox
import random
import time

DLC_INFO = {
    'nombre': 'Pack de Juegos Mega',
    'version': '2.1.0',
    'autor': 'Thisisfenix',
    'descripcion': '7 minijuegos épicos: Snake, Flappy Cat, Simon Says, Whack-a-Mole, Space Invaders, Memory y Runner'
}

def inicializar(mascota):
    """Inicializa el DLC y añade los juegos al menú"""
    print(f"[DLC] {DLC_INFO['nombre']} v{DLC_INFO['version']} cargado")

def obtener_interfaz(mascota):
    """Retorna la interfaz completa del DLC para que Mascota Saltarina la muestre"""
    import tkinter as tk
    
    # Crear ventana principal del DLC
    win = tk.Toplevel(mascota.root)
    win.title(f"🎮 {DLC_INFO['nombre']}")
    win.geometry("500x650")
    win.configure(bg='#0a0e27')
    win.attributes('-topmost', True)
    
    # Header
    header = tk.Frame(win, bg='#6366f1')
    header.pack(fill='x')
    tk.Label(header, text=f"🎮 {DLC_INFO['nombre']}", bg='#6366f1', fg='#ffffff', 
             font=('Arial', 18, 'bold')).pack(pady=15)
    
    # Info
    info_frame = tk.Frame(win, bg='#1e1b4b')
    info_frame.pack(fill='x', padx=20, pady=10)
    tk.Label(info_frame, text=f"v{DLC_INFO['version']} por {DLC_INFO['autor']}", 
             bg='#1e1b4b', fg='#a6a6a6', font=('Arial', 9)).pack(pady=5)
    tk.Label(info_frame, text=DLC_INFO['descripcion'], bg='#1e1b4b', fg='#cdd6f4', 
             font=('Arial', 10), wraplength=450).pack(pady=5)
    
    # Canvas con scroll
    canvas = tk.Canvas(win, bg='#0a0e27', highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg='#0a0e27')
    
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw", width=480)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=10)
    scrollbar.pack(side="right", fill="y")
    
    # Lista de juegos con sus configuraciones
    juegos = [
        ("🐍 Snake", juego_snake, '#a6e3a1', 'Clásico juego de la serpiente'),
        ("🐱 Flappy Cat", juego_flappy, '#f9e2af', 'Esquiva obstáculos volando'),
        ("🎨 Simon Says", juego_simon, '#cba6f7', 'Memoriza la secuencia'),
        ("🔨 Whack-a-Mole", juego_whack, '#f38ba8', 'Golpea los topos'),
        ("👾 Space Invaders", juego_space_invaders, '#89dceb', 'Defiende la Tierra'),
        ("🧠 Memory", juego_memory, '#cba6f7', 'Encuentra las parejas'),
        ("🏃 Runner", juego_runner, '#f9e2af', 'Corre sin parar')
    ]
    
    for nombre, func, color, desc in juegos:
        card = tk.Frame(frame, bg='#313244', relief='solid', bd=1)
        card.pack(pady=8, padx=10, fill='x')
        
        # Contenido
        content = tk.Frame(card, bg='#313244')
        content.pack(fill='x', padx=15, pady=10)
        
        # Nombre y descripción
        tk.Label(content, text=nombre, bg='#313244', fg=color, 
                font=('Arial', 12, 'bold')).pack(anchor='w')
        tk.Label(content, text=desc, bg='#313244', fg='#a6a6a6', 
                font=('Arial', 8)).pack(anchor='w', pady=(2, 8))
        
        # Botón
        tk.Button(content, text="▶ Jugar", command=lambda f=func: f(mascota), 
                 bg=color, fg='#1e1e2e', font=('Arial', 10, 'bold'), 
                 relief='flat', cursor='hand2', width=15).pack()
    
    # Botón cerrar
    tk.Button(win, text="Cerrar", command=win.destroy, bg='#6c7086', fg='#cdd6f4',
             font=('Arial', 11, 'bold'), width=20, height=2).pack(pady=15)
    
    return win

def juego_snake(mascota):
    """Juego Snake clásico"""
    win = tk.Toplevel(mascota.root)
    win.title("🐍 Snake")
    win.geometry("400x450")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="🐍 SNAKE", bg='#1e1e2e', fg='#a6e3a1', font=('Arial', 16, 'bold')).pack(pady=10)
    
    canvas = tk.Canvas(win, width=400, height=400, bg='#0a0e27', highlightthickness=0)
    canvas.pack()
    
    # Estado del juego
    snake = [(200, 200), (190, 200), (180, 200)]
    direccion = [10, 0]
    comida = [random.randint(0, 39) * 10, random.randint(0, 39) * 10]
    puntos = [0]
    jugando = [True]
    
    def mover():
        if not jugando[0]:
            return
        
        # Nueva cabeza
        cabeza = (snake[0][0] + direccion[0], snake[0][1] + direccion[1])
        
        # Verificar colisión con paredes
        if cabeza[0] < 0 or cabeza[0] >= 400 or cabeza[1] < 0 or cabeza[1] >= 400:
            jugando[0] = False
            messagebox.showinfo("Game Over", f"¡Perdiste! Puntos: {puntos[0]}")
            win.destroy()
            return
        
        # Verificar colisión consigo mismo
        if cabeza in snake:
            jugando[0] = False
            messagebox.showinfo("Game Over", f"¡Perdiste! Puntos: {puntos[0]}")
            win.destroy()
            return
        
        snake.insert(0, cabeza)
        
        # Verificar si comió
        if cabeza[0] == comida[0] and cabeza[1] == comida[1]:
            puntos[0] += 10
            comida[0] = random.randint(0, 39) * 10
            comida[1] = random.randint(0, 39) * 10
        else:
            snake.pop()
        
        # Dibujar
        canvas.delete('all')
        for x, y in snake:
            canvas.create_rectangle(x, y, x+10, y+10, fill='#a6e3a1', outline='')
        canvas.create_rectangle(comida[0], comida[1], comida[0]+10, comida[1]+10, fill='#f38ba8', outline='')
        canvas.create_text(200, 20, text=f"Puntos: {puntos[0]}", fill='#89b4fa', font=('Arial', 12, 'bold'))
        
        win.after(100, mover)
    
    def cambiar_dir(event):
        if event.keysym == 'Up' and direccion[1] == 0:
            direccion[0], direccion[1] = 0, -10
        elif event.keysym == 'Down' and direccion[1] == 0:
            direccion[0], direccion[1] = 0, 10
        elif event.keysym == 'Left' and direccion[0] == 0:
            direccion[0], direccion[1] = -10, 0
        elif event.keysym == 'Right' and direccion[0] == 0:
            direccion[0], direccion[1] = 10, 0
    
    win.bind('<Key>', cambiar_dir)
    win.focus_set()
    mover()

def juego_flappy(mascota):
    """Flappy Cat"""
    from PIL import Image, ImageTk
    
    win = tk.Toplevel(mascota.root)
    win.title("🐱 Flappy Cat")
    win.geometry("400x550")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="🐱 FLAPPY CAT", bg='#1e1e2e', fg='#f9e2af', font=('Arial', 16, 'bold')).pack(pady=10)
    
    canvas = tk.Canvas(win, width=400, height=500, bg='#89dceb', highlightthickness=0)
    canvas.pack()
    
    # Cargar imagen de la mascota
    try:
        img = Image.open(mascota.imagen_path)
        img = img.resize((40, 40), Image.Resampling.LANCZOS)
        mascota_img = ImageTk.PhotoImage(img)
    except:
        mascota_img = None
    
    # Estado
    cat_y = [250]
    velocidad = [0]
    obstaculos = [[400, random.randint(150, 300)]]
    puntos = [0]
    jugando = [True]
    
    def saltar(event):
        velocidad[0] = -8
    
    def actualizar():
        if not jugando[0]:
            return
        
        # Física
        velocidad[0] += 0.5
        cat_y[0] += velocidad[0]
        
        # Mover obstáculos
        for obs in obstaculos:
            obs[0] -= 3
        
        # Añadir nuevos obstáculos
        if obstaculos[-1][0] < 200:
            obstaculos.append([400, random.randint(150, 300)])
            puntos[0] += 1
        
        # Eliminar obstáculos fuera
        if obstaculos[0][0] < -50:
            obstaculos.pop(0)
        
        # Colisiones
        if cat_y[0] < 20 or cat_y[0] > 480:
            jugando[0] = False
            messagebox.showinfo("Game Over", f"Puntos: {puntos[0]}")
            win.destroy()
            return
        
        for obs in obstaculos:
            if 150 < obs[0] < 200:
                if cat_y[0] < obs[1] - 75 or cat_y[0] > obs[1] + 75:
                    jugando[0] = False
                    messagebox.showinfo("Game Over", f"Puntos: {puntos[0]}")
                    win.destroy()
                    return
        
        # Dibujar
        canvas.delete('all')
        canvas.create_text(200, 30, text=f"Puntos: {puntos[0]}", fill='#1e1e2e', font=('Arial', 14, 'bold'))
        
        # Dibujar mascota del usuario o emoji
        if mascota_img:
            canvas.create_image(175, cat_y[0], image=mascota_img)
        else:
            canvas.create_text(175, cat_y[0], text='🐱', font=('Arial', 30))
        
        for obs in obstaculos:
            canvas.create_rectangle(obs[0], 0, obs[0]+50, obs[1]-75, fill='#a6e3a1', outline='')
            canvas.create_rectangle(obs[0], obs[1]+75, obs[0]+50, 500, fill='#a6e3a1', outline='')
        
        win.after(30, actualizar)
    
    win.bind('<space>', saltar)
    win.focus_set()
    actualizar()

def juego_simon(mascota):
    """Simon Says"""
    win = tk.Toplevel(mascota.root)
    win.title("🎨 Simon Says")
    win.geometry("450x550")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="🎨 SIMON SAYS", bg='#1e1e2e', fg='#cba6f7', font=('Arial', 16, 'bold')).pack(pady=10)
    tk.Label(win, text="Memoriza la secuencia y repite los colores", bg='#1e1e2e', fg='#a6a6a6', font=('Arial', 9)).pack(pady=5)
    
    colores = ['#f38ba8', '#a6e3a1', '#89b4fa', '#f9e2af']
    secuencia = []
    jugador = []
    nivel = [0]
    mostrando = [False]
    
    info = tk.Label(win, text=f"Nivel: {nivel[0]}", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 14, 'bold'))
    info.pack(pady=10)
    
    frame = tk.Frame(win, bg='#1e1e2e')
    frame.pack(pady=20)
    
    botones = []
    for i in range(4):
        btn = tk.Button(frame, bg=colores[i], width=12, height=6, state='disabled',
                       command=lambda c=i: click_color(c), relief='raised', bd=3)
        btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        botones.append(btn)
    
    def nueva_ronda():
        secuencia.append(random.randint(0, 3))
        nivel[0] = len(secuencia)
        info.config(text=f"Nivel: {nivel[0]}")
        jugador.clear()
        win.after(500, mostrar_secuencia)
    
    def mostrar_secuencia():
        mostrando[0] = True
        for btn in botones:
            btn.config(state='disabled')
        
        def mostrar_color(idx):
            if idx < len(secuencia):
                color_idx = secuencia[idx]
                botones[color_idx].config(relief='sunken', bg='#ffffff')
                win.after(400, lambda: botones[color_idx].config(relief='raised', bg=colores[color_idx]))
                win.after(700, lambda: mostrar_color(idx + 1))
            else:
                mostrando[0] = False
                for btn in botones:
                    btn.config(state='normal')
        
        mostrar_color(0)
    
    def click_color(idx):
        if mostrando[0]:
            return
        
        # Feedback visual
        botones[idx].config(relief='sunken')
        win.after(200, lambda: botones[idx].config(relief='raised'))
        
        jugador.append(idx)
        
        if jugador[-1] != secuencia[len(jugador)-1]:
            messagebox.showinfo("Game Over", f"¡Perdiste! Llegaste al nivel {nivel[0]}")
            win.destroy()
            return
        
        if len(jugador) == len(secuencia):
            for btn in botones:
                btn.config(state='disabled')
            win.after(1000, nueva_ronda)
    
    btn_iniciar = tk.Button(win, text="▶ Iniciar Juego", command=nueva_ronda, bg='#89b4fa', fg='#1e1e2e',
             font=('Arial', 12, 'bold'), width=20, height=2).pack(pady=15)

def juego_whack(mascota):
    """Whack-a-Mole"""
    win = tk.Toplevel(mascota.root)
    win.title("🔨 Whack-a-Mole")
    win.geometry("450x500")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="🔨 WHACK-A-MOLE", bg='#1e1e2e', fg='#f38ba8', font=('Arial', 16, 'bold')).pack(pady=10)
    
    puntos = [0]
    tiempo = [30]
    jugando = [True]
    topo_activo = [-1]
    
    info = tk.Label(win, text=f"Puntos: {puntos[0]} | Tiempo: {tiempo[0]}s", bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 12))
    info.pack(pady=10)
    
    frame = tk.Frame(win, bg='#1e1e2e')
    frame.pack(pady=20)
    
    botones = []
    for i in range(9):
        btn = tk.Button(frame, text="⚫", width=8, height=4, bg='#313244', fg='#6c7086',
                       font=('Arial', 20), command=lambda idx=i: golpear(idx))
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        botones.append(btn)
    
    def mostrar_topo():
        if not jugando[0]:
            return
        
        # Limpiar topo anterior
        if topo_activo[0] != -1:
            botones[topo_activo[0]].config(text="⚫", bg='#313244')
        
        topo_activo[0] = random.randint(0, 8)
        botones[topo_activo[0]].config(text="🐹", bg='#a6e3a1')
        
        win.after(1000, mostrar_topo)
    
    def golpear(idx):
        if idx == topo_activo[0] and jugando[0]:
            puntos[0] += 10
            info.config(text=f"Puntos: {puntos[0]} | Tiempo: {tiempo[0]}s")
            botones[idx].config(text="💥", bg='#f38ba8')
            # Limpiar efecto después de 200ms
            win.after(200, lambda: botones[idx].config(text="⚫", bg='#313244') if jugando[0] else None)
            topo_activo[0] = -1
    
    def countdown():
        if tiempo[0] > 0 and jugando[0]:
            tiempo[0] -= 1
            info.config(text=f"Puntos: {puntos[0]} | Tiempo: {tiempo[0]}s")
            win.after(1000, countdown)
        elif tiempo[0] == 0:
            jugando[0] = False
            messagebox.showinfo("Fin", f"¡Juego terminado! Puntos: {puntos[0]}")
            win.destroy()
    
    mostrar_topo()
    countdown()

# Menú de juegos (DEPRECADO - usar obtener_interfaz)
def mostrar_menu_juegos(mascota):
    """DEPRECADO: Usa obtener_interfaz() en su lugar"""
    return obtener_interfaz(mascota)

def juego_space_invaders(mascota):
    """Space Invaders simplificado"""
    win = tk.Toplevel(mascota.root)
    win.title("👾 Space Invaders")
    win.geometry("400x550")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="👾 SPACE INVADERS", bg='#1e1e2e', fg='#89dceb', font=('Arial', 16, 'bold')).pack(pady=10)
    tk.Label(win, text="Flechas: Mover | Espacio: Disparar", bg='#1e1e2e', fg='#a6a6a6', font=('Arial', 9)).pack()
    
    canvas = tk.Canvas(win, width=400, height=480, bg='#0a0e27', highlightthickness=0)
    canvas.pack()
    
    # Estado
    nave_x = [180]
    aliens = []
    balas = []
    puntos = [0]
    jugando = [True]
    
    # Crear aliens
    for fila in range(4):
        for col in range(8):
            aliens.append({'x': col * 45 + 20, 'y': fila * 40 + 50, 'activo': True})
    
    def manejar_tecla(event):
        if not jugando[0]:
            return
        
        if event.keysym == 'Left' and nave_x[0] > 0:
            nave_x[0] -= 20
        elif event.keysym == 'Right' and nave_x[0] < 370:
            nave_x[0] += 20
        elif event.keysym == 'space':
            balas.append({'x': nave_x[0] + 15, 'y': 430})
    
    def actualizar():
        if not jugando[0]:
            return
        
        # Mover balas
        for bala in balas:
            bala['y'] -= 10
        balas[:] = [b for b in balas if b['y'] > 0]
        
        # Colisiones
        for bala in balas[:]:
            for alien in aliens:
                if alien['activo']:
                    if (alien['x'] < bala['x'] < alien['x'] + 30 and
                        alien['y'] < bala['y'] < alien['y'] + 30):
                        alien['activo'] = False
                        if bala in balas:
                            balas.remove(bala)
                        puntos[0] += 10
                        break
        
        # Victoria
        if all(not a['activo'] for a in aliens):
            jugando[0] = False
            messagebox.showinfo("¡Victoria!", f"¡Ganaste! Puntos: {puntos[0]}")
            win.destroy()
            return
        
        # Dibujar
        canvas.delete('all')
        canvas.create_text(200, 20, text=f"Puntos: {puntos[0]}", fill='#89b4fa', font=('Arial', 14, 'bold'))
        canvas.create_polygon(nave_x[0], 450, nave_x[0]+15, 430, nave_x[0]+30, 450, fill='#a6e3a1', outline='')
        
        for alien in aliens:
            if alien['activo']:
                canvas.create_text(alien['x']+15, alien['y']+15, text='👾', font=('Arial', 20))
        
        for bala in balas:
            canvas.create_rectangle(bala['x'], bala['y'], bala['x']+3, bala['y']+10, fill='#f9e2af', outline='')
        
        win.after(30, actualizar)
    
    win.bind('<KeyPress>', manejar_tecla)
    win.focus_set()
    actualizar()

def juego_memory(mascota):
    """Juego de memoria con cartas"""
    win = tk.Toplevel(mascota.root)
    win.title("🧠 Memory")
    win.geometry("450x550")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    tk.Label(win, text="🧠 MEMORY GAME", bg='#1e1e2e', fg='#cba6f7', font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Símbolos
    simbolos = ['🐱', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼'] * 2
    random.shuffle(simbolos)
    
    cartas = []
    seleccionadas = []
    parejas = [0]
    intentos = [0]
    
    info = tk.Label(win, text=f"Parejas: {parejas[0]}/8 | Intentos: {intentos[0]}", 
                   bg='#1e1e2e', fg='#cdd6f4', font=('Arial', 12))
    info.pack(pady=10)
    
    frame = tk.Frame(win, bg='#1e1e2e')
    frame.pack(pady=20)
    
    def click_carta(idx):
        if len(seleccionadas) >= 2 or cartas[idx]['revelada']:
            return
        
        cartas[idx]['btn'].config(text=cartas[idx]['simbolo'], bg='#89b4fa')
        cartas[idx]['revelada'] = True
        seleccionadas.append(idx)
        
        if len(seleccionadas) == 2:
            intentos[0] += 1
            info.config(text=f"Parejas: {parejas[0]}/8 | Intentos: {intentos[0]}")
            
            if cartas[seleccionadas[0]]['simbolo'] == cartas[seleccionadas[1]]['simbolo']:
                parejas[0] += 1
                info.config(text=f"Parejas: {parejas[0]}/8 | Intentos: {intentos[0]}")
                seleccionadas.clear()
                
                if parejas[0] == 8:
                    messagebox.showinfo("¡Victoria!", f"¡Ganaste en {intentos[0]} intentos!")
                    win.destroy()
            else:
                win.after(1000, ocultar_cartas)
    
    def ocultar_cartas():
        for idx in seleccionadas:
            cartas[idx]['btn'].config(text='❓', bg='#313244')
            cartas[idx]['revelada'] = False
        seleccionadas.clear()
    
    for i in range(16):
        btn = tk.Button(frame, text='❓', width=6, height=3, bg='#313244', fg='#cdd6f4',
                       font=('Arial', 16), command=lambda idx=i: click_carta(idx))
        btn.grid(row=i//4, column=i%4, padx=5, pady=5)
        cartas.append({'btn': btn, 'simbolo': simbolos[i], 'revelada': False})

def juego_runner(mascota):
    """Endless Runner - Estilo dinosaurio de Google mejorado"""
    from PIL import Image, ImageTk
    
    win = tk.Toplevel(mascota.root)
    win.title("🏃 Runner")
    win.geometry("700x500")
    win.configure(bg='#1e1e2e')
    win.attributes('-topmost', True)
    
    # Header
    tk.Label(win, text="🏃 DINO RUNNER", bg='#1e1e2e', fg='#f9e2af', font=('Arial', 18, 'bold')).pack(pady=10)
    
    # Canvas
    canvas = tk.Canvas(win, width=700, height=350, bg='#f7f7f7', highlightthickness=0)
    canvas.pack(pady=10)
    
    # Cargar imagen de la mascota
    mascota_img = None
    try:
        img = Image.open(mascota.imagen_path)
        img = img.resize((45, 45), Image.Resampling.LANCZOS)
        mascota_img = ImageTk.PhotoImage(img)
    except:
        pass
    
    # Estado
    jugador_y = [250]
    saltando = [False]
    velocidad_y = [0]
    obstaculos = []
    nubes = [[650, 60], [500, 100], [350, 80]]
    suelo_x = [0]
    puntos = [0]
    velocidad = [6]
    jugando = [False]
    iniciado = [False]
    
    # IA adaptativa
    historial_saltos = []  # Guarda cuándo salta el jugador
    dificultad_ia = [0.5]  # 0=fácil, 1=difícil
    ultimo_salto = [0]
    
    # Pantalla inicio
    def calcular_distancia_ia():
        """IA decide distancia entre obstáculos según habilidad del jugador"""
        # Si el jugador es bueno (dificultad alta), obstáculos más cerca
        if dificultad_ia[0] > 0.7:
            return random.randint(250, 350)
        elif dificultad_ia[0] > 0.5:
            return random.randint(300, 450)
        else:
            # Jugador novato, más espacio
            return random.randint(400, 550)
    
    def decidir_obstaculo_ia():
        """IA decide qué obstáculo poner según el comportamiento del jugador"""
        # Primeros 3 obstáculos siempre fáciles
        if puntos[0] < 3:
            return 'bajo'
        
        # Si el jugador no ha saltado recientemente, poner obstáculo fácil
        if puntos[0] - ultimo_salto[0] > 3:
            return 'bajo'
        
        # Si el jugador es bueno, mezclar obstáculos difíciles
        if dificultad_ia[0] > 0.7:
            return random.choice(['bajo', 'alto', 'doble', 'doble'])
        elif dificultad_ia[0] > 0.5:
            return random.choice(['bajo', 'bajo', 'alto', 'doble'])
        else:
            # Jugador novato, más obstáculos fáciles
            return random.choice(['bajo', 'bajo', 'bajo', 'alto'])
    
    def mostrar_inicio():
        canvas.delete('all')
        # Cielo y suelo
        canvas.create_rectangle(0, 0, 700, 300, fill='#87ceeb', outline='')
        canvas.create_rectangle(0, 300, 700, 350, fill='#8b7355', outline='')
        canvas.create_line(0, 300, 700, 300, fill='#654321', width=3)
        
        # Título
        canvas.create_text(350, 100, text="🏃 DINO RUNNER", fill='#ffffff', 
                          font=('Arial', 32, 'bold'), anchor='center')
        canvas.create_text(350, 150, text="Presiona ESPACIO para saltar", fill='#ffffff', 
                          font=('Arial', 14), anchor='center')
        canvas.create_text(350, 180, text="Esquiva los obstáculos", fill='#ffffff', 
                          font=('Arial', 12), anchor='center')
        
        # Mascota preview
        if mascota_img:
            canvas.create_image(350, 240, image=mascota_img)
        else:
            canvas.create_rectangle(330, 220, 370, 260, fill='#535353', outline='')
    
    def iniciar_juego():
        if not iniciado[0]:
            iniciado[0] = True
            jugando[0] = True
            obstaculos.clear()
            obstaculos.append({'x': 700, 'tipo': random.choice(['bajo', 'alto', 'doble'])})
            puntos[0] = 0
            velocidad[0] = 6
            actualizar()
    
    def saltar(event):
        if not iniciado[0]:
            iniciar_juego()
        elif not saltando[0] and jugador_y[0] >= 250:
            saltando[0] = True
            velocidad_y[0] = -16
            # IA aprende: registra el salto y ajusta dificultad
            if len(obstaculos) > 0:
                distancia = obstaculos[0]['x'] - 90
                historial_saltos.append(distancia)
                # Si salta muy temprano o tarde, reduce dificultad
                if distancia > 150 or distancia < 30:
                    dificultad_ia[0] = max(0.3, dificultad_ia[0] - 0.05)
                else:
                    # Si salta bien, aumenta dificultad
                    dificultad_ia[0] = min(1.0, dificultad_ia[0] + 0.02)
            ultimo_salto[0] = puntos[0]
    
    def actualizar():
        if not jugando[0]:
            return
        
        # Física salto
        if saltando[0]:
            velocidad_y[0] += 1.2
            jugador_y[0] += velocidad_y[0]
            if jugador_y[0] >= 250:
                jugador_y[0] = 250
                saltando[0] = False
                velocidad_y[0] = 0
        
        # Mover suelo
        suelo_x[0] -= velocidad[0]
        if suelo_x[0] <= -50:
            suelo_x[0] = 0
        
        # Mover nubes
        for nube in nubes:
            nube[0] -= 2
            if nube[0] < -50:
                nube[0] = 750
                nube[1] = random.randint(50, 120)
        
        # Mover obstáculos
        for obs in obstaculos:
            obs['x'] -= velocidad[0]
        
        # Añadir obstáculos con IA adaptativa
        if len(obstaculos) == 0 or obstaculos[-1]['x'] < calcular_distancia_ia():
            tipo = decidir_obstaculo_ia()
            obstaculos.append({'x': 700, 'tipo': tipo})
            puntos[0] += 1
            if puntos[0] % 10 == 0:
                velocidad[0] = min(12, velocidad[0] + 1)
        
        # Eliminar obstáculos
        obstaculos[:] = [o for o in obstaculos if o['x'] > -50]
        
        # Colisiones mejoradas
        for obs in obstaculos:
            if 70 < obs['x'] < 115:
                if obs['tipo'] == 'bajo' and jugador_y[0] + 45 > 255:
                    game_over()
                    return
                elif obs['tipo'] == 'alto' and jugador_y[0] < 200 and jugador_y[0] + 45 > 200:
                    game_over()
                    return
                elif obs['tipo'] == 'doble' and (jugador_y[0] + 45 > 255 or (jugador_y[0] < 200 and jugador_y[0] + 45 > 200)):
                    game_over()
                    return
        
        dibujar()
        win.after(30, actualizar)
    
    def dibujar():
        canvas.delete('all')
        
        # Cielo degradado
        canvas.create_rectangle(0, 0, 700, 300, fill='#87ceeb', outline='')
        
        # Nubes
        for nube in nubes:
            canvas.create_oval(nube[0], nube[1], nube[0]+40, nube[1]+25, fill='#ffffff', outline='')
            canvas.create_oval(nube[0]+20, nube[1]-5, nube[0]+60, nube[1]+20, fill='#ffffff', outline='')
            canvas.create_oval(nube[0]+40, nube[1], nube[0]+80, nube[1]+25, fill='#ffffff', outline='')
        
        # Suelo con textura
        canvas.create_rectangle(0, 300, 700, 350, fill='#8b7355', outline='')
        canvas.create_line(0, 300, 700, 300, fill='#654321', width=3)
        for i in range(int(suelo_x[0]), 700, 50):
            canvas.create_line(i, 300, i+20, 300, fill='#654321', width=2)
        
        # HUD
        canvas.create_text(650, 30, text=f"HI {puntos[0]:05d}", fill='#2c2c2c', 
                          font=('Courier', 14, 'bold'))
        canvas.create_text(650, 55, text=f"VEL: {int(velocidad[0])}", fill='#2c2c2c', 
                          font=('Courier', 10))
        
        # Jugador
        if mascota_img:
            canvas.create_image(90, jugador_y[0]+22, image=mascota_img)
        else:
            canvas.create_rectangle(70, jugador_y[0], 110, jugador_y[0]+45, fill='#535353', outline='')
        
        # Obstáculos variados
        for obs in obstaculos:
            if obs['tipo'] == 'bajo':
                # Cactus bajo
                canvas.create_rectangle(obs['x'], 270, obs['x']+25, 300, fill='#2d5016', outline='')
                canvas.create_rectangle(obs['x']+5, 260, obs['x']+12, 270, fill='#2d5016', outline='')
                canvas.create_rectangle(obs['x']+13, 260, obs['x']+20, 270, fill='#2d5016', outline='')
            elif obs['tipo'] == 'alto':
                # Pterodáctilo volador
                canvas.create_text(obs['x']+15, 210, text='🦅', font=('Arial', 30))
            elif obs['tipo'] == 'doble':
                # Cactus doble
                canvas.create_rectangle(obs['x'], 265, obs['x']+15, 300, fill='#2d5016', outline='')
                canvas.create_rectangle(obs['x']+20, 270, obs['x']+35, 300, fill='#2d5016', outline='')
    
    def game_over():
        jugando[0] = False
        canvas.create_rectangle(200, 120, 500, 230, fill='#1e1e2e', outline='#f9e2af', width=3)
        canvas.create_text(350, 150, text="GAME OVER", fill='#f38ba8', 
                          font=('Arial', 24, 'bold'))
        canvas.create_text(350, 190, text=f"Puntos: {puntos[0]}", fill='#a6e3a1', 
                          font=('Arial', 16))
        win.after(2000, win.destroy)
    
    # Botón iniciar
    btn_frame = tk.Frame(win, bg='#1e1e2e')
    btn_frame.pack(pady=10)
    
    def click_iniciar():
        btn_iniciar.config(state='disabled')
        iniciar_juego()
    
    btn_iniciar = tk.Button(btn_frame, text="▶ INICIAR JUEGO", command=click_iniciar,
                           bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 14, 'bold'),
                           width=20, height=2, relief='flat', cursor='hand2')
    btn_iniciar.pack()
    
    win.bind('<space>', saltar)
    win.bind('<KeyPress-space>', saltar)
    win.focus_set()
    mostrar_inicio()

# Agregar botón al menú de juegos de la mascota
def agregar_boton_menu(mascota):
    """Agrega el botón del DLC al menú de juegos"""
    try:
        # Buscar el frame de juegos y agregar botón
        tk.Button(mascota.pagina_juegos, text="🎮 Pack de Juegos DLC", command=lambda: mostrar_menu_juegos(mascota),
                 bg='#89b4fa', fg='#1e1e2e', font=('Arial', 12, 'bold'), relief='flat', cursor='hand2').pack(pady=10)
    except:
        pass
