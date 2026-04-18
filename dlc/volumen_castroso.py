# DLC: Slider de Volumen Castroso
# Control de volumen del sistema ULTRA CASTROSO

DLC_INFO = {
    "nombre": "Volumen Castroso",
    "version": "2.0.0",
    "autor": "Fenix",
    "descripcion": "Control de volumen ULTRA CASTROSO con minijuegos, binario, spam y más",
    "tipo": "utilidad"
}

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import subprocess
import os

class VolumenCastroso:
    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🔊 Volumen Castroso")
        self.ventana.geometry("450x600")
        self.ventana.configure(bg='#1a1a2e')
        self.ventana.resizable(False, False)
        
        # Control de volumen con nircmd
        self.volume = None
        vol_actual = 50
        
        # Verificar si nircmd está disponible
        if os.path.exists('nircmd.exe'):
            self.volume = 'nircmd'
            # Intentar obtener volumen actual
            try:
                result = subprocess.run(['nircmd.exe', 'getsysvolume'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    vol_actual = int(float(result.stdout.strip()) / 655.35)
            except:
                pass
        
        # Título
        tk.Label(self.ventana, text="🔊 VOLUMEN CASTROSO 2.0", bg='#1a1a2e', fg='#ff6b6b',
                font=('Arial', 16, 'bold')).pack(pady=15)
        
        # Volumen actual
        self.label_volumen = tk.Label(self.ventana, text=f"{vol_actual}%", 
                                      bg='#1a1a2e', fg='#00ff41',
                                      font=('Arial', 36, 'bold'))
        self.label_volumen.pack(pady=10)
        
        # Modos castrosos
        tk.Label(self.ventana, text="Elige tu tortura:", bg='#1a1a2e', fg='#a6a6a6',
                font=('Arial', 10)).pack(pady=5)
        
        btn_frame = tk.Frame(self.ventana, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🎮 Juego Items", command=self.modo_items,
                 bg='#a6e3a1', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=0, column=0, padx=3, pady=3)
        
        tk.Button(btn_frame, text="❌⭕ 3 en Raya", command=self.modo_tres_raya,
                 bg='#89b4fa', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=0, column=1, padx=3, pady=3)
        
        tk.Button(btn_frame, text="💻 Binario", command=self.modo_binario,
                 bg='#f9e2af', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=0, column=2, padx=3, pady=3)
        
        tk.Button(btn_frame, text="📢 Spam", command=self.modo_spam,
                 bg='#f38ba8', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=1, column=0, padx=3, pady=3)
        
        tk.Button(btn_frame, text="🎲 Ruleta", command=self.modo_ruleta,
                 bg='#cba6f7', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=1, column=1, padx=3, pady=3)
        
        tk.Button(btn_frame, text="🧠 Matemáticas", command=self.modo_matematicas,
                 bg='#fab387', fg='#1e1e2e', font=('Arial', 9, 'bold'),
                 width=12, relief='flat', cursor='hand2').grid(row=1, column=2, padx=3, pady=3)
        
        # Slider normal (para los valientes)
        tk.Label(self.ventana, text="O usa el slider normal (aburrido):", bg='#1a1a2e', fg='#6c7086',
                font=('Arial', 8, 'italic')).pack(pady=5)
        
        self.slider = ttk.Scale(self.ventana, from_=0, to=100, orient='horizontal',
                               command=self.cambiar_volumen, length=300)
        self.slider.set(vol_actual)
        self.slider.pack(pady=10)
        
        tk.Button(self.ventana, text="❌ Cerrar", command=self.ventana.destroy,
                 bg='#1a1a2e', fg='#ffffff', font=('Arial', 11, 'bold'),
                 width=20, relief='flat', cursor='hand2', bd=2,
                 highlightbackground='#e94560', highlightthickness=2).pack(pady=15)
    
    def cambiar_volumen(self, valor):
        if self.volume == 'nircmd':
            try:
                vol = int(float(valor) * 655.35)
                subprocess.run(['nircmd.exe', 'setsysvolume', str(vol)], 
                             shell=True, capture_output=True)
            except:
                pass
        self.label_volumen.config(text=f"{int(float(valor))}%")
    
    def modo_items(self):
        """Juego de recoger items para subir volumen"""
        win = tk.Toplevel(self.ventana)
        win.title("🎮 Juego Items")
        win.geometry("400x450")
        win.configure(bg='#1e1e2e')
        win.attributes('-topmost', True)
        
        tk.Label(win, text="🎮 RECOGE ITEMS", bg='#1e1e2e', fg='#a6e3a1',
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(win, text="Usa flechas para moverte", bg='#1e1e2e', fg='#a6a6a6',
                font=('Arial', 9)).pack()
        
        canvas = tk.Canvas(win, width=400, height=350, bg='#0a0e27', highlightthickness=0)
        canvas.pack(pady=10)
        
        jugador_x = [180]
        items = []
        volumen_juego = [0]
        jugando = [True]
        
        def crear_item():
            if jugando[0]:
                items.append({'x': random.randint(20, 370), 'y': 0, 'tipo': random.choice(['+5', '+10', '-5'])})
                win.after(1500, crear_item)
        
        def mover(event):
            if event.keysym == 'Left' and jugador_x[0] > 0:
                jugador_x[0] -= 20
            elif event.keysym == 'Right' and jugador_x[0] < 370:
                jugador_x[0] += 20
        
        def actualizar():
            if not jugando[0]:
                return
            
            for item in items:
                item['y'] += 5
            
            # Colisiones
            for item in items[:]:
                if 300 < item['y'] < 340 and abs(item['x'] - jugador_x[0]) < 25:
                    if item['tipo'] == '+5':
                        volumen_juego[0] = min(100, volumen_juego[0] + 5)
                    elif item['tipo'] == '+10':
                        volumen_juego[0] = min(100, volumen_juego[0] + 10)
                    else:
                        volumen_juego[0] = max(0, volumen_juego[0] - 5)
                    items.remove(item)
                    self.cambiar_volumen(volumen_juego[0])
            
            items[:] = [i for i in items if i['y'] < 350]
            
            # Dibujar
            canvas.delete('all')
            canvas.create_text(200, 20, text=f"Volumen: {volumen_juego[0]}%", fill='#89b4fa',
                             font=('Arial', 12, 'bold'))
            canvas.create_rectangle(jugador_x[0], 310, jugador_x[0]+30, 340, fill='#a6e3a1', outline='')
            
            for item in items:
                color = '#00ff41' if '+' in item['tipo'] else '#ff0000'
                canvas.create_text(item['x'], item['y'], text=item['tipo'], fill=color,
                                 font=('Arial', 16, 'bold'))
            
            win.after(30, actualizar)
        
        win.bind('<Key>', mover)
        win.focus_set()
        crear_item()
        actualizar()
    
    def modo_tres_raya(self):
        """3 en raya contra IA - ganas = cambias volumen"""
        win = tk.Toplevel(self.ventana)
        win.title("❌⭕ 3 en Raya")
        win.geometry("350x450")
        win.configure(bg='#1e1e2e')
        win.attributes('-topmost', True)
        
        tk.Label(win, text="❌⭕ 3 EN RAYA", bg='#1e1e2e', fg='#89b4fa',
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(win, text="Gana para cambiar el volumen", bg='#1e1e2e', fg='#a6a6a6',
                font=('Arial', 9)).pack()
        
        tablero = ['' for _ in range(9)]
        botones = []
        
        frame = tk.Frame(win, bg='#1e1e2e')
        frame.pack(pady=20)
        
        def verificar_ganador():
            lineas = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
            for a, b, c in lineas:
                if tablero[a] == tablero[b] == tablero[c] != '':
                    return tablero[a]
            return None
        
        def ia_juega():
            vacios = [i for i in range(9) if tablero[i] == '']
            if vacios:
                pos = random.choice(vacios)
                tablero[pos] = 'O'
                botones[pos].config(text='O', fg='#f38ba8', state='disabled')
        
        def click(idx):
            if tablero[idx] == '':
                tablero[idx] = 'X'
                botones[idx].config(text='X', fg='#89b4fa', state='disabled')
                
                ganador = verificar_ganador()
                if ganador == 'X':
                    vol = tk.simpledialog.askinteger("Ganaste!", "Ingresa volumen (0-100):",
                                                     minvalue=0, maxvalue=100)
                    if vol is not None:
                        self.cambiar_volumen(vol)
                    win.destroy()
                    return
                
                ia_juega()
                ganador = verificar_ganador()
                if ganador == 'O':
                    messagebox.showinfo("Perdiste", "La IA ganó! Volumen aleatorio")
                    self.cambiar_volumen(random.randint(0, 100))
                    win.destroy()
        
        for i in range(9):
            btn = tk.Button(frame, text='', width=6, height=3, bg='#313244', fg='#cdd6f4',
                           font=('Arial', 20, 'bold'), command=lambda idx=i: click(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            botones.append(btn)
    
    def modo_binario(self):
        """Ingresa volumen en binario"""
        win = tk.Toplevel(self.ventana)
        win.title("💻 Binario")
        win.geometry("400x300")
        win.configure(bg='#1e1e2e')
        win.attributes('-topmost', True)
        
        tk.Label(win, text="💻 MODO BINARIO", bg='#1e1e2e', fg='#f9e2af',
                font=('Arial', 14, 'bold')).pack(pady=15)
        tk.Label(win, text="Ingresa el volumen en binario (0-1100100 = 0-100)",
                bg='#1e1e2e', fg='#a6a6a6', font=('Arial', 9)).pack(pady=5)
        
        entry = tk.Entry(win, font=('Courier', 16), bg='#313244', fg='#00ff41',
                        insertbackground='#00ff41', width=15, justify='center')
        entry.pack(pady=20)
        
        def convertir():
            try:
                binario = entry.get().strip()
                if not all(c in '01' for c in binario):
                    messagebox.showerror("Error", "Solo 0 y 1 permitidos")
                    return
                decimal = int(binario, 2)
                if 0 <= decimal <= 100:
                    self.cambiar_volumen(decimal)
                    messagebox.showinfo("✅", f"Volumen: {decimal}%")
                    win.destroy()
                else:
                    messagebox.showerror("Error", "Debe ser entre 0 y 100")
            except:
                messagebox.showerror("Error", "Binario inválido")
        
        tk.Button(win, text="✅ Aplicar", command=convertir, bg='#a6e3a1', fg='#1e1e2e',
                 font=('Arial', 12, 'bold'), width=15).pack(pady=10)
    
    def modo_spam(self):
        """Spam de confirmaciones"""
        def spam_recursivo(nivel=0):
            if nivel >= 5:
                vol = random.randint(0, 100)
                self.cambiar_volumen(vol)
                messagebox.showinfo("🎉", f"Finalmente! Volumen: {vol}%")
                return
            
            respuesta = messagebox.askyesno(
                f"Confirmación {nivel+1}/5",
                f"¿Estás SEGURO que quieres cambiar el volumen?\n\n"
                f"Nivel de confirmación: {nivel+1}/5"
            )
            if respuesta:
                spam_recursivo(nivel + 1)
            else:
                messagebox.showwarning("Cancelado", "Operación cancelada. Volumen aleatorio!")
                self.cambiar_volumen(random.randint(0, 100))
        
        spam_recursivo()
    
    def modo_ruleta(self):
        """Ruleta de volumen"""
        win = tk.Toplevel(self.ventana)
        win.title("🎲 Ruleta")
        win.geometry("350x400")
        win.configure(bg='#1e1e2e')
        win.attributes('-topmost', True)
        
        tk.Label(win, text="🎲 RULETA DE VOLUMEN", bg='#1e1e2e', fg='#cba6f7',
                font=('Arial', 14, 'bold')).pack(pady=15)
        
        label_num = tk.Label(win, text="?", bg='#1e1e2e', fg='#00ff41',
                            font=('Arial', 72, 'bold'))
        label_num.pack(pady=40)
        
        def girar():
            for i in range(20):
                num = random.randint(0, 100)
                label_num.config(text=str(num))
                win.update()
                win.after(50 + i*10)
            
            final = random.randint(0, 100)
            label_num.config(text=str(final))
            self.cambiar_volumen(final)
            messagebox.showinfo("🎲", f"Volumen: {final}%")
            win.destroy()
        
        tk.Button(win, text="🎲 GIRAR", command=girar, bg='#cba6f7', fg='#1e1e2e',
                 font=('Arial', 14, 'bold'), width=15, height=2).pack(pady=20)
    
    def modo_matematicas(self):
        """Resuelve operación matemática"""
        a = random.randint(10, 50)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '*'])
        
        if op == '+':
            resultado = a + b
        elif op == '-':
            resultado = a - b
        else:
            resultado = a * b
        
        respuesta = tk.simpledialog.askinteger(
            "🧠 Matemáticas",
            f"Resuelve para cambiar el volumen:\n\n{a} {op} {b} = ?"
        )
        
        if respuesta == resultado:
            vol = tk.simpledialog.askinteger("Correcto!", "Ingresa volumen (0-100):",
                                            minvalue=0, maxvalue=100)
            if vol is not None:
                self.cambiar_volumen(vol)
        else:
            messagebox.showerror("Incorrecto", f"Era {resultado}. Volumen aleatorio!")
            self.cambiar_volumen(random.randint(0, 100))

def inicializar(mascota):
    print(f"[DLC] {DLC_INFO['nombre']} v{DLC_INFO['version']} cargado")

def obtener_interfaz(mascota):
    try:
        return VolumenCastroso(mascota.root)
    except Exception as e:
        mascota.mostrar_texto(f"❌ Error: {str(e)}")
        return None
