using MascotaSaltarina.SDK;

public class SpeedBoostMod : IMod
{
    public string Name => "Speed Boost";
    public string Version => "1.0.0";
    public string Author => "Ankush Team";
    public string Description => "Aumenta la velocidad de la mascota x2";

    private double originalSpeed = 3.0;
    private bool isBoosted = false;

    public void Initialize(IModHost host)
    {
        originalSpeed = host.Speed;
        host.Speed = originalSpeed * 2;
        isBoosted = true;
        host.ShowText("⚡ Speed Boost activado! x2");
    }

    public void Update(IModHost host) { }

    public void OnClick(IModHost host)
    {
        if (isBoosted)
        {
            host.Speed += 0.5;
            host.ShowText($"⚡ Velocidad: {host.Speed:F1}");
        }
    }

    public void Shutdown(IModHost host)
    {
        if (isBoosted)
        {
            host.Speed = originalSpeed;
            host.ShowText("⚡ Speed Boost desactivado");
            isBoosted = false;
        }
    }
}
