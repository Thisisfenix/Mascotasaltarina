# ⚡ Instalación Rápida - Ankush Cat

## 🎯 Elige tu versión

### 🐍 Versión Python (Multiplataforma)
```bash
# 1. Instalar Python 3.8+ desde python.org
# 2. Abrir terminal en la carpeta del proyecto
pip install -r requirements.txt
python mascota_saltarina.py
```

### 💎 Versión C# (Solo Windows, Mejor Rendimiento)
```bash
# 1. Instalar .NET 8.0+ desde dotnet.microsoft.com
# 2. Abrir terminal en la carpeta MascotaSaltarinaCS
cd MascotaSaltarinaCS
dotnet run
```

---

## 🚀 Compilar Ejecutable

### Python → EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico mascota_saltarina.py
# Ejecutable en: dist/mascota_saltarina.exe
```

### C# → EXE
```bash
cd MascotaSaltarinaCS
compilar.bat
# Ejecutable en: publish/AnkushCat.exe
```

---

## ❓ Problemas Comunes

### Python: "No module named 'PIL'"
```bash
pip install pillow pygame psutil requests pywin32 pystray
```

### C#: "dotnet no se reconoce"
1. Instala .NET SDK desde https://dotnet.microsoft.com/download
2. Reinicia la terminal
3. Verifica: `dotnet --version`

### "No se encuentra la imagen"
- Verifica que la carpeta `assets` esté en el mismo directorio
- Verifica que exista `assets/AnkushCat.png`

---

## 📚 Más Información

- **Documentación completa**: [README_PROYECTO_COMPLETO.md](README_PROYECTO_COMPLETO.md)
- **Comparación Python vs C#**: [COMPARACION_PYTHON_VS_CSHARP.md](COMPARACION_PYTHON_VS_CSHARP.md)
- **Guía de migración**: [GUIA_MIGRACION.md](GUIA_MIGRACION.md)

---

**¡Listo! Ahora disfruta de tu mascota virtual** 🐱✨
