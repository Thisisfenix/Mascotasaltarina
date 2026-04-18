# 🔧 Cómo crear un Mod para Ankush Cat v3.0

## Pasos

1. Crea un archivo `.cs` en esta carpeta (`mods/`)
2. Implementa la interfaz `IMod` del SDK
3. Inicia el juego — se compilará automáticamente
4. Actívalo desde el panel **Mods** dentro del juego

## Plantilla mínima

```csharp
using MascotaSaltarina.SDK;

public class MiMod : IMod
{
    public string Name        => "Mi Mod";
    public string Version     => "1.0.0";
    public string Author      => "YO";
    public string Description => "Descripción corta";

    public void Initialize(IModHost host) { host.ShowText("Mod cargado!"); }
    public void Update(IModHost host)     { /* ~60fps */ }
    public void OnClick(IModHost host)    { /* al hacer clic en la mascota */ }
    public void Shutdown(IModHost host)   { }
}
```

## API disponible (IModHost)

| Propiedad/Método | Descripción |
|---|---|
| `PosX`, `PosY` | Posición de la mascota (lectura/escritura) |
| `Speed` | Velocidad |
| `Size` | Tamaño en píxeles |
| `Opacity` | Opacidad (0.0 - 1.0) |
| `ClickCount` | Clicks esta sesión |
| `TotalClicks` | Clicks totales históricos |
| `ShowText(text)` | Muestra un globo de texto |
| `Explode()` | Hace explotar la mascota |
| `RandomPosition()` | Posición aleatoria |
| `CenterScreen()` | Centrar en pantalla |
| `CreateClone()` | Crea un clon |
| `RemoveClones()` | Elimina todos los clones |
| `PlaySound(path)` | Reproduce un audio (ruta relativa a assets/) |
| `Hunger`, `Happiness` | Stats de la mascota |
| `Level`, `XP` | Nivel y experiencia |
| `GainXP(amount)` | Dar XP |

## Notas
- El `.cs` se recompila solo si es más nuevo que el `.dll` generado
- Si hay errores de compilación, aparecen en la mascota como texto
- Puedes usar cualquier clase de .NET 8 y WPF
