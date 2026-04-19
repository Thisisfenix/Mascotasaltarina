# Cambios en v3.0.1

## 🐛 Fix Crítico: Instalador y Sistema de Actualizaciones

### Problema 1: Instalador no descargaba assets
El instalador solo descargaba los archivos ejecutables y DLLs, pero **no descargaba las carpetas `assets/`, `mods/` y `dlcs/`**, causando que la aplicación no funcionara correctamente después de la instalación.

### Problema 2: Actualizaciones no descargaban assets
El sistema de actualizaciones automáticas tampoco descargaba las carpetas assets/mods/dlcs, solo actualizaba los ejecutables.

### Solución
- ✅ **Instalador**: Implementado sistema de descarga recursiva usando GitHub API
- ✅ **UpdateChecker**: Agregada descarga de assets/mods/dlcs en actualizaciones
- ✅ **UI**: Cambiado botón "Abrir Updater.exe" → "Abrir Instalador"
- ✅ **Archivos**: Reemplazado `Updater.exe` (Python) por `AnkushCatInstaller.exe` (C#)

### Descarga Completa
Ahora tanto el instalador como las actualizaciones descargan:
- ✅ Archivos principales (EXE, DLLs)
- ✅ Carpeta `assets/` completa (imágenes, audio, videos)
- ✅ Carpeta `mods/` con ejemplos
- ✅ Carpeta `dlcs/` con ejemplos
- ✅ Subcarpetas recursivamente

### Cambios Técnicos

**AnkushCatInstaller/MainWindow.xaml.cs**:
- Agregado método `DescargarCarpeta()` que usa GitHub API
- Agregado método `DescargarSubcarpeta()` para recursión
- Barra de progreso: 0-50% archivos, 50-95% carpetas
- User-Agent agregado para GitHub API

**MascotaSaltarinaCS/UpdateChecker.cs**:
- Agregado método `DescargarCarpetaGitHub()` 
- Agregado método `DescargarSubcarpetaGitHub()`
- Descarga assets/mods/dlcs después de archivos principales
- User-Agent agregado para GitHub API

**MascotaSaltarinaCS/MainWindow.xaml.cs**:
- Cambiado referencia de `Updater.exe` → `AnkushCatInstaller.exe`
- Actualizado texto del botón: "Abrir Instalador"

**MascotaSaltarinaCS/publish/assets/updater/**:
- ❌ Eliminado `Updater.exe` (Python viejo)
- ✅ Agregado `AnkushCatInstaller.exe` (C# nuevo)

## 📦 Otros Cambios Incluidos

### Fixes de v3.0.0 (incluidos en esta release)
- 🐛 Fix: Error Window_Closing al cerrar aplicación
- 🐛 Fix: Error ScriptCompiler con DLLs en uso
- 🐛 Fix: UpdateChecker URL actualizada a `publish/`
- ✨ Limpieza: 0 advertencias de compilación
- 📁 Workflow simplificado: Solo `publish/` (eliminado `publish_fd/`)

## 📊 Estadísticas

- **Tamaño instalador**: 174 KB
- **Archivos descargados**: ~100+ (antes: ~15)
- **Carpetas incluidas**: assets/, mods/, dlcs/
- **Compilación**: 0 Advertencias, 0 Errores ✅

## 🚀 Proceso Mejorado

### Instalación (AnkushCatInstaller.exe)
1. Descargar archivos principales (0-50%)
2. Descargar assets/ completo (50-70%)
3. Descargar mods/ (70-85%)
4. Descargar dlcs/ (85-95%)
5. ✅ Aplicación lista para usar

### Actualización Automática (UpdateChecker)
1. Detectar nueva versión
2. Descargar archivos principales
3. Descargar assets/mods/dlcs actualizados
4. Aplicar actualización con batch script
5. Reiniciar aplicación

## 📝 Archivos Modificados

- `AnkushCatInstaller/MainWindow.xaml.cs` - Sistema de descarga mejorado
- `AnkushCatInstaller/AnkushCatInstaller.exe` - Recompilado (174 KB)
- `MascotaSaltarinaCS/UpdateChecker.cs` - Descarga de assets/mods/dlcs
- `MascotaSaltarinaCS/MainWindow.xaml.cs` - Botón actualizado
- `MascotaSaltarinaCS/Rebornversion.txt` - Versión 3.0.1
- `MascotaSaltarinaCS/publish/assets/updater/` - AnkushCatInstaller.exe
- `HolaGissel/update_info.json` - Changelog actualizado
- `HolaGissel/assets/updater/AnkushCatInstaller.exe` - Actualizado
- `MascotaSaltarinaCS/compilar.bat` - Mensaje actualizado a v3.0.1

## 🔗 URLs

- **Instalador**: https://raw.githubusercontent.com/Thisisfenix/Mascotasaltarina/main/HolaGissel/assets/updater/AnkushCatInstaller.exe
- **Archivos**: https://raw.githubusercontent.com/Thisisfenix/Mascotasaltarina/main/MascotaSaltarinaCS/publish/

## ⚠️ Nota Importante

Si instalaste la versión 3.0.0:
1. El sistema de actualizaciones automáticas descargará v3.0.1
2. Se descargarán todos los assets/mods/dlcs faltantes
3. La aplicación funcionará correctamente después de actualizar

O puedes descargar manualmente el nuevo instalador v3.0.1 y ejecutarlo.
