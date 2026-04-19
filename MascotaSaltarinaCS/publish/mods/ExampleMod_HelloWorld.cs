using MascotaSaltarina.SDK;

public class HelloWorldMod : IMod
{
    public string Name => "Hello World Mod";
    public string Version => "1.0.0";
    public string Author => "Ankush Team";
    public string Description => "Mod de ejemplo que muestra un mensaje de bienvenida";

    private IModHost? api;

    public void Initialize(IModHost host)
    {
        api = host;
        api.ShowText("👋 Hello World Mod activado!");
    }

    public void Update(IModHost host) { }

    public void OnClick(IModHost host)
    {
        host.ShowText("¡Hola desde el mod!");
    }

    public void Shutdown(IModHost host)
    {
        host.ShowText("👋 Hello World Mod desactivado");
    }
}
