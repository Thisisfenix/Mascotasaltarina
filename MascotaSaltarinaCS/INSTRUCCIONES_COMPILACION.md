# 🔨 Instrucciones de Compilación - Ankush Cat C#

## 📋 Requisitos Previos

### 1. Instalar .NET SDK

**Windows:**
1. Ve a: https://dotnet.microsoft.com/download
2. Descarga ".NET 8.0 SDK" (no solo Runtime)
3. Ejecuta el instalador
4. Reinicia la terminal/PowerShell

**Verificar instalación:**
```bash
dotnet --version
# Debe mostrar: 8.0.x o superior
```

---

## 🚀 Método 1: Compilación Rápida (Recomendado)

### Usando el Script Batch

```bash
# 1. Abrir terminal en la carpeta MascotaSaltarinaCS
cd MascotaSaltarinaCS

# 2. Ejecutar script de compilación
compilar.bat

# 3. El ejecutable estará en: publish/AnkushCat.exe
```

**Ventajas:**
- ✅ Rápido y simple
- ✅ Ejecutable pequeño (~15 MB)
- ❌ Requiere .NET instalado en el PC donde se ejecute

---

## 📦 Método 2: Compilación Standalone

### Ejecutable que NO requiere .NET

```bash
# 1. Abrir terminal en la carpeta MascotaSaltarinaCS
cd MascotaSaltarinaCS

# 2. Ejecutar script standalone
compilar_standalone.bat

# 3. El ejecutable estará en: publish-standalone/AnkushCat.exe
```

**Ventajas:**
- ✅ Funciona en cualquier PC Windows 10/11
- ✅ No requiere instalar .NET
- ❌ Ejecutable más grande (~60-80 MB)

---

## 💻 Método 3: Compilación Manual

### Paso a Paso con Comandos

```bash
# 1. Navegar a la carpeta
cd MascotaSaltarinaCS

# 2. Restaurar paquetes NuGet
dotnet restore

# 3. Compilar en modo Release
dotnet build --configuration Release

# 4. Publicar (versión normal)
dotnet publish --configuration Release --output ./publish --self-contained false

# O publicar (versión standalone)
dotnet publish --configuration Release --output ./publish-standalone --self-contained true --runtime win-x64 /p:PublishSingleFile=true
```

---

## 🎨 Método 4: Usar Visual Studio

### Con IDE Visual Studio 2022

1. **Abrir el proyecto**
   - Abre Visual Studio 2022
   - File > Open > Project/Solution
   - Selecciona `MascotaSaltarinaCS.csproj`

2. **Restaurar paquetes**
   - Visual Studio lo hace automáticamente
   - O: Tools > NuGet Package Manager > Restore

3. **Compilar**
   - Build > Build Solution (Ctrl+Shift+B)
   - O presiona F6

4. **Ejecutar**
   - Debug > Start Without Debugging (Ctrl+F5)
   - O presiona F5 para debug

5. **Publicar**
   - Build > Publish MascotaSaltarinaCS
   - Selecciona carpeta de destino
   - Configura opciones (self-contained, etc.)
   - Click en "Publish"

---

## 📁 Estructura de Salida

### Después de compilar con `compilar.bat`:
```
MascotaSaltarinaCS/
└── publish/
    ├── AnkushCat.exe          # Ejecutable principal
    ├── AnkushCat.dll
    ├── NAudio.dll
    ├── Newtonsoft.Json.dll
    ├── assets/                # Copiar manualmente
    ├── version.txt            # Copiar manualmente
    └── icon.ico               # Copiar manualmente
```

### Después de compilar con `compilar_standalone.bat`:
```
MascotaSaltarinaCS/
└── publish-standalone/
    ├── AnkushCat.exe          # Ejecutable único (~60-80 MB)
    ├── assets/                # Copiado automáticamente
    ├── version.txt            # Copiado automáticamente
    └── icon.ico               # Copiado automáticamente
```

---

## ⚠️ Importante: Copiar Assets

### Si usas `compilar.bat` (versión normal):

**Debes copiar manualmente:**
```bash
# Desde la raíz del proyecto
xcopy /E /I assets publish\assets
copy version.txt publish\
copy icon.ico publish\
```

**O en PowerShell:**
```powershell
Copy-Item -Path assets -Destination publish\assets -Recurse
Copy-Item -Path version.txt -Destination publish\
Copy-Item -Path icon.ico -Destination publish\
```

### Si usas `compilar_standalone.bat`:
✅ Los assets se copian automáticamente

---

## 🧪 Probar el Ejecutable

### Versión Normal (requiere .NET):
```bash
cd publish
AnkushCat.exe
```

### Versión Standalone:
```bash
cd publish-standalone
AnkushCat.exe
```

---

## 🐛 Solución de Problemas

### Error: "dotnet no se reconoce como comando"
**Solución:**
1. Instala .NET SDK (no solo Runtime)
2. Reinicia la terminal
3. Verifica con `dotnet --version`

### Error: "No se pudo restaurar los paquetes"
**Solución:**
```bash
# Limpiar caché de NuGet
dotnet nuget locals all --clear

# Restaurar de nuevo
dotnet restore
```

### Error: "No se encuentra NAudio"
**Solución:**
```bash
# Instalar manualmente
dotnet add package NAudio --version 2.2.1
dotnet add package Newtonsoft.Json --version 13.0.3
```

### Error: "No se carga la imagen"
**Solución:**
- Verifica que la carpeta `assets` esté en el mismo directorio que el .exe
- Verifica que exista `assets/AnkushCat.png`
- Copia los assets manualmente si es necesario

### Error: "La aplicación no se inicia"
**Solución:**
1. Verifica que .NET 8.0 Runtime esté instalado (si usas versión normal)
2. Ejecuta desde terminal para ver errores:
   ```bash
   cd publish
   .\AnkushCat.exe
   ```
3. Revisa los mensajes de error

---

## 📊 Comparación de Métodos

| Método | Tamaño | Requiere .NET | Velocidad | Dificultad |
|--------|--------|---------------|-----------|------------|
| **compilar.bat** | ~15 MB | ✅ Sí | ⚡⚡⚡ Rápido | ⭐ Fácil |
| **compilar_standalone.bat** | ~60-80 MB | ❌ No | ⚡⚡ Medio | ⭐ Fácil |
| **Manual (dotnet)** | Variable | Configurable | ⚡⚡ Medio | ⭐⭐ Medio |
| **Visual Studio** | Variable | Configurable | ⚡ Lento | ⭐⭐⭐ Avanzado |

---

## 🎯 Recomendaciones

### Para Desarrollo:
- Usa **Visual Studio** o `dotnet run`
- No necesitas compilar cada vez
- Cambios se reflejan inmediatamente

### Para Distribución Personal:
- Usa **compilar.bat**
- Ejecutable pequeño
- Asume que tienes .NET instalado

### Para Distribución Pública:
- Usa **compilar_standalone.bat**
- Funciona en cualquier PC
- No requiere instalaciones adicionales

---

## 📦 Crear Instalador (Opcional)

### Usando Inno Setup

1. **Descargar Inno Setup**: https://jrsoftware.org/isinfo.php

2. **Crear script** `installer.iss`:
```iss
[Setup]
AppName=Ankush Cat
AppVersion=2.0.0
DefaultDirName={pf}\AnkushCat
DefaultGroupName=Ankush Cat
OutputDir=installer
OutputBaseFilename=AnkushCat_Setup

[Files]
Source: "publish-standalone\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Ankush Cat"; Filename: "{app}\AnkushCat.exe"
Name: "{commondesktop}\Ankush Cat"; Filename: "{app}\AnkushCat.exe"
```

3. **Compilar instalador** con Inno Setup

---

## ✅ Checklist de Compilación

Antes de distribuir, verifica:

- [ ] El ejecutable se inicia correctamente
- [ ] La imagen se carga y se mueve
- [ ] Los sonidos funcionan
- [ ] El panel de control responde
- [ ] Los efectos visuales funcionan
- [ ] No hay errores en la consola
- [ ] La carpeta assets está incluida
- [ ] El archivo version.txt está incluido
- [ ] El icono se muestra correctamente

---

## 🚀 Comandos Rápidos de Referencia

```bash
# Restaurar paquetes
dotnet restore

# Compilar
dotnet build

# Ejecutar sin compilar
dotnet run

# Compilar Release
dotnet build -c Release

# Publicar normal
dotnet publish -c Release -o ./publish

# Publicar standalone
dotnet publish -c Release -o ./publish-standalone --self-contained true --runtime win-x64 /p:PublishSingleFile=true

# Limpiar compilación
dotnet clean
```

---

## 📞 Ayuda Adicional

Si tienes problemas:
1. Revisa esta guía completa
2. Consulta [GUIA_MIGRACION.md](../GUIA_MIGRACION.md)
3. Busca en Issues del repositorio
4. Crea un nuevo Issue con detalles

---

**¡Buena suerte con la compilación!** 🎉
