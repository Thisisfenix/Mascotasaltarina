# Cambios en v3.0.1

## 🐛 Fix Crítico: Instalador

### Problema
El instalador solo descargaba los archivos ejecutables y DLLs, pero **no descargaba las carpetas `assets/`, `mods/` y `dlcs/`**, causando que la aplicación no funcionara correctamente después de la instalación.

### Solución
- Implementado sistema de descarga recursiva usando GitHub API
- El instalador ahora descarga automáticamente:
  - ✅ Archivos principales (EXE, DLLs)
  - ✅ Carpeta `assets/` completa (imágenes, audio, videos)
  - ✅ Carpeta `mods/` con ejemplos
  - ✅ Carpeta `dlcs/` con ejemplos
  - ✅ Subcarpetas recursivamente

### Cambios Técnicos
- Agregado método `DescargarCarpeta()` que usa GitHub API
- Agregado método `DescargarSubcarpeta()` para recursión
- Barra de progreso actualizada: 0-50% archivos, 50-95% carpetas
- User-Agent agregado para GitHub API
- Versión actualizada a 3.0.1 en `ankushcat_version.txt`

**Archivo**: `AnkushCatInstaller/MainWindow.xaml.cs`

## 📦 Otros Cambios Incluidos

### Fixes de v3.0.0 (incluidos en esta release)
- 🐛 Fix: Error Window_Closing al cerrar aplicación
- 🐛 Fix: Error ScriptCompiler con DLLs en uso
- 🐛 Fix: UpdateChecker URL actualizada a `publish/`
- ✨ Limpieza: 0 advertencias de compilación
- 📁 Workflow simplificado: Solo `publish/` (eliminado `publish_fd/`)

## 📊 Estadísticas

- **Tamaño instalador**: 174 KB (antes: 171 KB)
- **Archivos descargados**: ~100+ (antes: ~15)
- **Carpetas incluidas**: assets/, mods/, dlcs/
- **Compilación**: 0 Advertencias, 0 Errores ✅

## 🚀 Proceso de Instalación Mejorado

### Antes (v3.0.0)
1. Descargar 15 archivos (solo EXE y DLLs)
2. ❌ Faltaban assets, mods, dlcs
3. ❌ Aplicación no funcionaba correctamente

### Ahora (v3.0.1)
1. Descargar archivos principales (0-50%)
2. Descargar assets/ completo (50-70%)
3. Descargar mods/ (70-85%)
4. Descargar dlcs/ (85-95%)
5. ✅ Aplicación lista para usar

## 📝 Archivos Modificados

- `AnkushCatInstaller/MainWindow.xaml.cs` - Sistema de descarga mejorado
- `AnkushCatInstaller/AnkushCatInstaller.exe` - Recompilado (174 KB)
- `MascotaSaltarinaCS/Rebornversion.txt` - Versión 3.0.1
- `HolaGissel/update_info.json` - Changelog actualizado
- `HolaGissel/assets/updater/AnkushCatInstaller.exe` - Actualizado
- `MascotaSaltarinaCS/compilar.bat` - Mensaje actualizado a v3.0.1

## 🔗 URLs

- **Instalador**: https://raw.githubusercontent.com/Thisisfenix/Mascotasaltarina/main/HolaGissel/assets/updater/AnkushCatInstaller.exe
- **Archivos**: https://raw.githubusercontent.com/Thisisfenix/Mascotasaltarina/main/MascotaSaltarinaCS/publish/

## ⚠️ Nota Importante

Si instalaste la versión 3.0.0, necesitas:
1. Descargar el nuevo instalador v3.0.1
2. Ejecutarlo en la misma carpeta
3. Los assets/mods/dlcs se descargarán automáticamente

O simplemente espera a que el sistema de actualizaciones automáticas descargue la nueva versión.
