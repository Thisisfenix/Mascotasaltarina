# 🔧 Mods para Ankush Cat

Los mods son scripts en C# que se cargan dinámicamente y pueden modificar el comportamiento de la mascota.

## 📁 Ubicación
Coloca tus archivos `.cs` en esta carpeta: `mods/`

## 🎯 Mods de Ejemplo Incluidos

### 1. **ExampleMod_HelloWorld.cs**
- **Descripción**: Mod básico que muestra mensajes
- **Funcionalidad**: 
  - Muestra "Hello World" al activarse
  - Responde a clicks con mensajes
- **Ideal para**: Aprender la estructura básica de un mod

### 2. **ExampleMod_SpeedBoost.cs**
- **Descripción**: Aumenta la velocidad de la mascota
- **Funcionalidad**:
  - Duplica la velocidad al activarse
  - Cada click aumenta la velocidad +0.5
  - Restaura velocidad original al desactivarse
- **Ideal para**: Ver cómo modificar propiedades de la mascota

### 3. **ExampleMod_Rainbow.cs**
- **Descripción**: Activa modo arcoiris con rastro
- **Funcionalidad**:
  - Activa modo arcoiris automáticamente
  - Activa el rastro de colores
  - Cuenta clicks y muestra mensajes cada 10 clicks
- **Ideal para**: Combinar múltiples efectos visuales

## 🛠️ Crear tu Propio Mod

### Estructura Básica

```csharp
using MascotaSaltarina.SDK;

public class MiMod : IMod
{
    public string Name => "Mi Mod Genial";
    public string Version => "1.0.0";
    public string Author => "Tu Nombre";
    public string Description => "Descripción de tu mod";

    private IFloatingImageAPI? api;

    public void OnActivate(IFloatingImageAPI floatingImageAPI)
    {
        api = floatingImageAPI;
        // Código al activar el mod
        api.ShowText("¡Mod activado!");
    }

    public void OnDeactivate()
    {
        // Código al desactivar el mod
        api?.ShowText("Mod desactivado");
    }

    public void OnClick()
    {
        // Código cuando el usuario hace click en la mascota
    }

    public void OnUpdate()
    {
        // Código que se ejecuta cada frame
    }
}
```

## 📚 API Disponible

### Métodos de IFloatingImageAPI

```csharp
// Mensajes
void ShowText(string text);
void LogInfo(string message);

// Propiedades
double GetSpeed();
void SetSpeed(double speed);
int GetSize();
void SetSize(int size);
double GetOpacity();
void SetOpacity(double opacity);

// Modos
bool GetGravityEnabled();
void SetGravityEnabled(bool enabled);
bool GetBounceEnabled();
void SetBounceEnabled(bool enabled);
bool GetDragEnabled();
void SetDragEnabled(bool enabled);
bool GetRotationEnabled();
void SetRotationEnabled(bool enabled);

// Efectos
void SetRainbowMode(bool enabled);
void SetTrailEnabled(bool enabled);

// Estadísticas
int GetClickCount();
int GetTotalClicks();
int GetClicksPerMinute();
string GetUptime();
```

## 🔄 Cómo Usar los Mods

1. **Cargar mods**: Ve a la página "Mods" en la aplicación
2. **Clic en "🔄 Reescanear mods"**: Detecta nuevos archivos .cs
3. **Activar/Desactivar**: Usa el checkbox junto a cada mod
4. **Ver errores**: Si un mod falla, revisa `ankushcat_log.txt`

## ⚠️ Notas Importantes

- Los mods se compilan en tiempo real usando Roslyn
- Si hay errores de compilación, aparecerán en el log
- Los mods pueden acceder a toda la API de la mascota
- Puedes tener múltiples mods activos simultáneamente
- Los cambios en archivos .cs requieren reescanear

## 🐛 Debugging

Si tu mod no funciona:

1. Revisa `ankushcat_log.txt` en la carpeta de instalación
2. Verifica que la clase implemente `IMod`
3. Asegúrate de que el archivo esté en la carpeta `mods/`
4. Usa `api.LogInfo()` para debug

## 💡 Ideas para Mods

- Cambiar el tamaño automáticamente
- Reproducir sonidos personalizados
- Crear patrones de movimiento únicos
- Modificar la opacidad según la hora
- Contador de clicks con objetivos
- Integración con APIs externas
- Efectos visuales personalizados
