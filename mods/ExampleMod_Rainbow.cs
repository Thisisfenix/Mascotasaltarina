using MascotaSaltarina.SDK;

public class RainbowTrailMod : IMod
{
    public string Name => "Rainbow Trail";
    public string Version => "1.0.0";
    public string Author => "Ankush Team";
    public string Description => "Activa modo arcoiris con rastro de colores";

    private int clickCount = 0;

    public void Initialize(IModHost host)
    {
        host.ShowText("🌈 Rainbow Trail activado!");
    }

    public void Update(IModHost host) { }

    public void OnClick(IModHost host)
    {
        clickCount++;
        if (clickCount % 10 == 0)
            host.ShowText($"🌈 {clickCount} clicks arcoiris!");
    }

    public void Shutdown(IModHost host)
    {
        host.ShowText("🌈 Rainbow Trail desactivado");
    }
}
