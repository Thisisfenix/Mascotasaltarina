# 📦 DLCs para Ankush Cat

Los DLCs son extensiones que añaden ventanas y funcionalidades adicionales a la aplicación.

## 📁 Ubicación
Coloca tus archivos `.cs` en esta carpeta: `dlcs/`

## 🎯 DLCs de Ejemplo Incluidos

### 1. **ExampleDLC_Stats.cs** 📊
- **Descripción**: Visor de estadísticas avanzadas
- **Funcionalidad**:
  - Muestra estadísticas en tiempo real
  - Clicks, velocidad, tamaño, opacidad
  - Modos activos
  - Tiempo de actividad
  - Botón de refrescar
- **Ideal para**: Ver toda la información de la mascota

### 2. **ExampleDLC_ColorPicker.cs** 🎨
- **Descripción**: Selector de colores para tintes
- **Funcionalidad**:
  - Paleta de 12 colores predefinidos
  - Aplica tintes de color a la mascota
  - Botón para quitar tinte
- **Ideal para**: Personalización visual

### 3. **ExampleDLC_Timer.cs** ⏱️
- **Descripción**: Temporizador Pomodoro
- **Funcionalidad**:
  - Temporizador configurable (25, 15, 5 minutos)
  - Técnica Pomodoro para productividad
  - Notificación al terminar
  - Controles de inicio/pausa
- **Ideal para**: Gestión del tiempo mientras trabajas

## 🛠️ Crear tu Propio DLC

### Estructura Básica

```csharp
using MascotaSaltarina.SDK;
using System.Windows;

public class MiDLC : IDlc
{
    public string Name => "Mi DLC Genial";
    public string Version => "1.0.0";
    public string Author => "Tu Nombre";
    public string Description => "Descripción de tu DLC";
    public string Icon => "🎮"; // Emoji que aparece en el botón

    private IFloatingImageAPI? api;

    public void Initialize(IFloatingImageAPI floatingImageAPI)
    {
        api = floatingImageAPI;
        api.LogInfo($"{Name} inicializado");
    }

    public void Open()
    {
        // Crear y mostrar tu ventana personalizada
        var window = new Window
        {
            Title = $"{Icon} {Name}",
            Width = 400,
            Height = 300,
            WindowStartupLocation = WindowStartupLocation.CenterScreen
        };

        // Añadir contenido a la ventana
        // ...

        window.Show();
    }
}
```

## 📚 API Disponible

### Métodos de IFloatingImageAPI

```csharp
// Mensajes y Log
void ShowText(string text);
void LogInfo(string message);

// Propiedades de la Mascota
double GetSpeed();
void SetSpeed(double speed);
int GetSize();
void SetSize(int size);
double GetOpacity();
void SetOpacity(double opacity);

// Estados y Modos
bool GetGravityEnabled();
void SetGravityEnabled(bool enabled);
bool GetBounceEnabled();
void SetBounceEnabled(bool enabled);
bool GetDragEnabled();
void SetDragEnabled(bool enabled);
bool GetRotationEnabled();
void SetRotationEnabled(bool enabled);

// Efectos Visuales
void SetRainbowMode(bool enabled);
void SetTrailEnabled(bool enabled);

// Estadísticas
int GetClickCount();
int GetTotalClicks();
int GetClicksPerMinute();
string GetUptime();
```

## 🎨 Crear Ventanas con WPF

Los DLCs pueden usar todo el poder de WPF para crear interfaces:

```csharp
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

public void Open()
{
    var window = new Window
    {
        Title = "Mi Ventana",
        Width = 400,
        Height = 300,
        Background = new SolidColorBrush(Color.FromRgb(0x1e, 0x1e, 0x2e))
    };

    var stack = new StackPanel { Margin = new Thickness(20) };

    // Añadir controles
    stack.Children.Add(new TextBlock
    {
        Text = "¡Hola desde mi DLC!",
        Foreground = Brushes.White,
        FontSize = 16
    });

    var button = new Button
    {
        Content = "Hacer algo",
        Height = 40
    };
    button.Click += (s, e) =>
    {
        api?.ShowText("¡Botón presionado!");
    };
    stack.Children.Add(button);

    window.Content = stack;
    window.Show();
}
```

## 🔄 Cómo Usar los DLCs

1. **Cargar DLCs**: Ve a la página "DLCs" en la aplicación
2. **Clic en "🔄 Reescanear DLCs"**: Detecta nuevos archivos .cs
3. **Abrir DLC**: Clic en el botón "▶ Abrir" junto al DLC
4. **Ver errores**: Si un DLC falla, revisa `ankushcat_log.txt`

## ⚠️ Notas Importantes

- Los DLCs se compilan en tiempo real usando Roslyn
- Pueden crear múltiples ventanas
- Tienen acceso completo a WPF
- Pueden usar timers, animaciones, etc.
- Los cambios en archivos .cs requieren reescanear

## 🐛 Debugging

Si tu DLC no funciona:

1. Revisa `ankushcat_log.txt` en la carpeta de instalación
2. Verifica que la clase implemente `IDlc`
3. Asegúrate de que el archivo esté en la carpeta `dlcs/`
4. Usa `api.LogInfo()` para debug
5. Verifica que tengas todos los `using` necesarios

## 💡 Ideas para DLCs

- **Calculadora**: Calculadora integrada
- **Notas**: Bloc de notas rápido
- **Clima**: Mostrar el clima actual
- **Música**: Reproductor de música
- **Tareas**: Lista de tareas pendientes
- **Calendario**: Calendario con recordatorios
- **Gráficas**: Visualización de estadísticas
- **Configuración avanzada**: Ajustes adicionales
- **Galería**: Visor de imágenes
- **Chat**: Integración con APIs de chat

## 🎮 DLC vs Mod

| Característica | Mod | DLC |
|---|---|---|
| **Propósito** | Modificar comportamiento de la mascota | Añadir ventanas/funcionalidades |
| **Interfaz** | `IMod` | `IDlc` |
| **Métodos** | `OnActivate`, `OnUpdate`, `OnClick` | `Initialize`, `Open` |
| **UI** | No tiene ventana propia | Crea ventanas WPF |
| **Uso típico** | Efectos, modos, modificadores | Herramientas, utilidades, paneles |

## 📖 Recursos

- [Documentación WPF](https://docs.microsoft.com/en-us/dotnet/desktop/wpf/)
- [Controles WPF](https://docs.microsoft.com/en-us/dotnet/desktop/wpf/controls/)
- SDK: `MascotaSaltarina.SDK/IDlc.cs`
