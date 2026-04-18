# 📦 Cómo crear un DLC para Ankush Cat v3.0

## Pasos

1. Crea un archivo `.cs` en esta carpeta (`dlcs/`)
2. Implementa la interfaz `IDlc` del SDK
3. Inicia el juego — se compilará automáticamente
4. Ábrelo desde el panel **DLCs** dentro del juego

## Plantilla mínima

```csharp
using System.Windows;
using System.Windows.Controls;
using MascotaSaltarina.SDK;

public class MiDlc : IDlc
{
    public string Name        => "Mi DLC";
    public string Version     => "1.0.0";
    public string Author      => "YO";
    public string Description => "Descripción";
    public string Icon        => "🎮";  // emoji que aparece en el panel

    public void Initialize(IModHost host) { }

    public Window OpenWindow(IModHost host)
    {
        var win = new Window { Title = "Mi DLC", Width = 400, Height = 300 };
        win.Content = new TextBlock { Text = "Hola desde mi DLC!" };
        return win;
    }

    public void Shutdown(IModHost host) { }
}
```

## Diferencia Mod vs DLC

| | Mod | DLC |
|---|---|---|
| Carpeta | `mods/` | `dlcs/` |
| Interfaz | `IMod` | `IDlc` |
| Tiene ventana propia | No | Sí |
| Se ejecuta en loop | Sí (Update) | No |
| Se activa/desactiva | Sí | Se abre/cierra |
