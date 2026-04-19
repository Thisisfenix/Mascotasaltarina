using MascotaSaltarina.SDK;
using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;

/// <summary>
/// DLC de ejemplo: Temporizador Pomodoro
/// </summary>
public class PomodoroTimerDLC : IDlc
{
    public string Name => "Pomodoro Timer";
    public string Version => "1.0.0";
    public string Author => "Ankush Team";
    public string Description => "Temporizador Pomodoro para productividad";
    public string Icon => "⏱️";

    private IModHost? api;
    private DispatcherTimer? timer;
    private int secondsRemaining = 0;
    private TextBlock? timeLabel;
    private Button? startBtn;
    private Button? stopBtn;

    public void Initialize(IModHost host)
    {
        api = host;
    }

    public Window OpenWindow(IModHost host)
    {
        api = host;

        var window = new Window
        {
            Title = "⏱️ Pomodoro Timer",
            Width = 350,
            Height = 300,
            WindowStartupLocation = WindowStartupLocation.CenterScreen,
            Background = new SolidColorBrush(Color.FromRgb(0x1e, 0x1e, 0x2e)),
            ResizeMode = ResizeMode.NoResize
        };

        var stack = new StackPanel
        {
            Margin = new Thickness(20),
            HorizontalAlignment = HorizontalAlignment.Center
        };

        stack.Children.Add(CreateLabel("⏱️ Temporizador Pomodoro", 16, true));
        stack.Children.Add(CreateLabel("Técnica de productividad", 11, false));

        timeLabel = new TextBlock
        {
            Text = "25:00",
            FontSize = 48,
            FontWeight = FontWeights.Bold,
            Foreground = new SolidColorBrush(Color.FromRgb(0x7C, 0x3A, 0xED)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 30, 0, 30)
        };
        stack.Children.Add(timeLabel);

        var presetStack = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 20)
        };
        presetStack.Children.Add(CreatePresetButton("25 min", 25));
        presetStack.Children.Add(CreatePresetButton("15 min", 15));
        presetStack.Children.Add(CreatePresetButton("5 min", 5));
        stack.Children.Add(presetStack);

        var controlStack = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            HorizontalAlignment = HorizontalAlignment.Center
        };

        startBtn = new Button
        {
            Content = "▶ Iniciar",
            Width = 100, Height = 40,
            Margin = new Thickness(5),
            Background = new SolidColorBrush(Color.FromRgb(0x22, 0xc5, 0x5e)),
            Foreground = Brushes.White,
            BorderThickness = new Thickness(0),
            Cursor = System.Windows.Input.Cursors.Hand
        };
        startBtn.Click += (s, e) => StartTimer();

        stopBtn = new Button
        {
            Content = "⏹ Detener",
            Width = 100, Height = 40,
            Margin = new Thickness(5),
            Background = new SolidColorBrush(Color.FromRgb(0xef, 0x44, 0x44)),
            Foreground = Brushes.White,
            BorderThickness = new Thickness(0),
            Cursor = System.Windows.Input.Cursors.Hand,
            IsEnabled = false
        };
        stopBtn.Click += (s, e) => StopTimer();

        controlStack.Children.Add(startBtn);
        controlStack.Children.Add(stopBtn);
        stack.Children.Add(controlStack);

        window.Content = stack;
        window.Closed += (s, e) => StopTimer();

        return window;
    }

    public void Shutdown(IModHost host)
    {
        StopTimer();
    }

    private Button CreatePresetButton(string label, int minutes)
    {
        var btn = new Button
        {
            Content = label,
            Width = 70, Height = 30,
            Margin = new Thickness(3),
            Background = new SolidColorBrush(Color.FromRgb(0x3A, 0x3A, 0x52)),
            Foreground = Brushes.White,
            BorderThickness = new Thickness(0),
            Cursor = System.Windows.Input.Cursors.Hand
        };
        btn.Click += (s, e) => SetTime(minutes);
        return btn;
    }

    private void SetTime(int minutes)
    {
        secondsRemaining = minutes * 60;
        UpdateDisplay();
    }

    private void StartTimer()
    {
        if (secondsRemaining == 0) secondsRemaining = 25 * 60;

        timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        timer.Tick += OnTimerTick;
        timer.Start();

        if (startBtn != null) startBtn.IsEnabled = false;
        if (stopBtn != null) stopBtn.IsEnabled = true;

        api?.ShowText("⏱️ Timer iniciado!");
    }

    private void StopTimer()
    {
        timer?.Stop();
        timer = null;
        if (startBtn != null) startBtn.IsEnabled = true;
        if (stopBtn != null) stopBtn.IsEnabled = false;
    }

    private void OnTimerTick(object? sender, EventArgs e)
    {
        secondsRemaining--;
        UpdateDisplay();

        if (secondsRemaining <= 0)
        {
            StopTimer();
            api?.ShowText("⏱️ ¡Tiempo terminado! 🎉");
            MessageBox.Show(
                "¡Tiempo terminado!\n\nToma un descanso de 5 minutos 😊",
                "⏱️ Pomodoro Completado",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }
    }

    private void UpdateDisplay()
    {
        if (timeLabel == null) return;
        int m = secondsRemaining / 60, s = secondsRemaining % 60;
        timeLabel.Text = $"{m:D2}:{s:D2}";
    }

    private TextBlock CreateLabel(string text, double size, bool bold) => new TextBlock
    {
        Text = text, FontSize = size,
        FontWeight = bold ? FontWeights.Bold : FontWeights.Normal,
        Foreground = Brushes.White,
        Margin = new Thickness(0, 5, 0, 5),
        TextWrapping = TextWrapping.Wrap,
        HorizontalAlignment = HorizontalAlignment.Center
    };
}
