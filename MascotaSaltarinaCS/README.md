# Ankush Cat - Mascota Saltarina (C# Version)

## 🐱 Descripción

Esta es la versión **reborn** en C# del proyecto original en Python "Mascota Saltarina". Mantiene las funcionalidades principales del proyecto original mientras aprovecha las ventajas de C# y WPF para Windows.

## ✨ Características

- **Mascota flotante interactiva** que se mueve por la pantalla
- **Sistema de rebote** con física realista
- **Efectos visuales**: rastro, partículas, explosiones
- **Sonidos** al hacer clic y eventos
- **Modos especiales**: perseguir cursor, gravedad, orbital, etc.
- **Panel de control moderno** con interfaz estilo Catppuccin
- **Sistema de estadísticas** para trackear clicks y tiempo de uso
- **Verificación automática de actualizaciones**

## 🚀 Requisitos

- .NET 8.0 o superior
- Windows 10/11
- Visual Studio 2022 o superior (recomendado)

## 📦 Dependencias

El proyecto utiliza las siguientes librerías NuGet:

- `NAudio` (2.2.1) - Para reproducción de audio
- `Newtonsoft.Json` (13.0.3) - Para manejo de datos JSON
- `System.Drawing.Common` (8.0.0) - Para manipulación de imágenes

## 🛠️ Instalación

### Opción 1: Compilar desde código fuente

1. Clona el repositorio o descarga los archivos
2. Abre el proyecto en Visual Studio 2022
3. Restaura los paquetes NuGet (automático al abrir)
4. Compila el proyecto (F6 o Build > Build Solution)
5. Ejecuta el programa (F5 o Debug > Start Debugging)

### Opción 2: Usar .NET CLI

```bash
cd MascotaSaltarinaCS
dotnet restore
dotnet build
dotnet run
```

## 📁 Estructura del Proyecto

```
MascotaSaltarinaCS/
├── App.xaml                    # Configuración de la aplicación
├── App.xaml.cs                 # Lógica de inicio
├── MainWindow.xaml             # Interfaz del panel de control
├── MainWindow.xaml.cs          # Lógica del panel de control
├── FloatingImage.cs            # Clase principal de la mascota flotante
├── UpdateChecker.cs            # Sistema de actualizaciones
├── MascotaSaltarinaCS.csproj   # Archivo de proyecto
├── README.md                   # Este archivo
├── icon.ico                    # Icono de la aplicación
├── version.txt                 # Versión actual
└── assets/                     # Recursos (imágenes, sonidos, etc.)
    ├── AnkushCat.png
    ├── sonidito.mp3
    ├── bounce.mp3
    ├── Explosion.mp3
    └── ...
```

## 🎮 Uso

1. **Ejecuta el programa** - Se abrirá el panel de control y aparecerá la mascota flotante
2. **Haz clic en la mascota** - Dirá frases aleatorias y aumentará el contador
3. **Usa el panel de control** para:
   - Ajustar velocidad, tamaño y opacidad
   - Activar/desactivar efectos (rebote, gravedad, rastro, sonidos)
   - Cambiar entre modos especiales (perseguir cursor, orbital, etc.)
   - Ver estadísticas de uso
4. **Clic derecho en la mascota** - Menú contextual con opciones rápidas

## 🎨 Características Principales

### Panel de Control
- **Principal**: Configuración básica (velocidad, tamaño, opacidad)
- **Efectos**: Efectos visuales y sonoros
- **Eventos**: Modos especiales de comportamiento
- **Acciones**: Botones para acciones rápidas
- **Stats**: Estadísticas de uso

### Modos Especiales
- 🎯 **Perseguir Cursor**: La mascota sigue el mouse
- 🌍 **Gravedad**: Simula física de gravedad
- 🎨 **Rastro**: Deja un rastro al moverse
- 💥 **Rebote Elástico**: Rebotes suaves y realistas

## 🔄 Diferencias con la Versión Python

### Ventajas de la versión C#:
- ✅ Mejor rendimiento nativo en Windows
- ✅ Interfaz más fluida con WPF
- ✅ Menor consumo de memoria
- ✅ Compilación a ejecutable nativo
- ✅ Mejor integración con Windows

### Características del Python original no implementadas (aún):
- Sistema de mods dinámicos
- Sistema de DLCs
- Algunos modos experimentales avanzados
- Sistema de logros y niveles

## 🚧 Desarrollo Futuro

Características planeadas:
- [ ] Sistema de plugins/mods
- [ ] Más efectos visuales
- [ ] Soporte para GIF animados
- [ ] Sistema de temas personalizables
- [ ] Múltiples mascotas simultáneas
- [ ] Sistema de logros
- [ ] Guardado de configuración

## 📝 Notas

- El proyecto Python original se mantiene intacto en la carpeta raíz
- Esta versión C# es una reescritura, no una conversión directa
- Algunas características pueden funcionar diferente debido a las diferencias entre Python/Tkinter y C#/WPF

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si quieres agregar características o mejorar el código:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto mantiene la misma licencia que el proyecto original.

## 👨‍💻 Autor

- **Versión Python Original**: [Thisisfenix](https://github.com/Thisisfenix)
- **Versión C# Reborn**: Conversión a C# con WPF

## 🙏 Agradecimientos

- Al creador original del proyecto Python
- A la comunidad de .NET y WPF
- A todos los que usan y disfrutan Ankush Cat

---

**Versión**: 2.0.0  
**Última actualización**: 2026
