@echo off
echo ========================================
echo   COMPILANDO UPDATER
echo ========================================
echo.

REM Instalar PyInstaller si no está instalado
echo Instalando PyInstaller...
pip install pyinstaller

echo.

REM Verificar que existe updater.py
if not exist updater.py (
    echo ERROR: No se encontro updater.py
    pause
    exit /b 1
)

REM Compilar updater
echo Compilando updater.py...
python -m PyInstaller --onefile --windowed --name="Updater" updater.py

echo Moviendo Updater.exe...
if not exist assets\updater mkdir assets\updater
move /Y dist\Updater.exe assets\updater\Updater.exe

echo Limpiando archivos temporales...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Updater.spec del Updater.spec

echo.
echo ========================================
echo   COMPILACION COMPLETADA
echo ========================================
echo.
echo Updater: assets\updater\Updater.exe
echo.
pause
