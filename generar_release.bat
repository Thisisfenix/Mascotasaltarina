@echo off
echo ========================================
echo   GENERANDO RELEASE v3.0
echo ========================================
echo.

REM Compilar el proyecto C#
echo [1/3] Compilando AnkushCat...
cd MascotaSaltarinaCS
dotnet build -c Release
if errorlevel 1 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)
cd ..

REM Crear el ZIP del bin usando PowerShell
echo [2/3] Creando AnkushCat_v3.zip...
powershell -Command "Compress-Archive -Path 'MascotaSaltarinaCS\bin\Release\net8.0-windows\*' -DestinationPath 'AnkushCat_v3.zip' -Force"
if errorlevel 1 (
    echo ERROR: Fallo la creacion del ZIP
    pause
    exit /b 1
)

REM Mover el ZIP a HolaGissel para que se suba al repo
if not exist HolaGissel mkdir HolaGissel
move /Y AnkushCat_v3.zip HolaGissel\AnkushCat_v3.zip

REM Compilar el updater
echo [3/3] Compilando Updater.exe...
pip install pyinstaller -q
python -m PyInstaller --onefile --windowed --name="Updater" updater.py
if exist dist\Updater.exe (
    if not exist assets\updater mkdir assets\updater
    move /Y dist\Updater.exe assets\updater\Updater.exe
    if not exist HolaGissel\assets\updater mkdir HolaGissel\assets\updater
    copy /Y assets\updater\Updater.exe HolaGissel\assets\updater\Updater.exe
)
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Updater.spec del Updater.spec

echo.
echo ========================================
echo   RELEASE GENERADO
echo ========================================
echo.
echo Archivos generados:
echo   HolaGissel\AnkushCat_v3.zip  (subir a GitHub)
echo   HolaGissel\assets\updater\Updater.exe
echo   HolaGissel\update_info.json  (ya actualizado)
echo.
echo Ahora haz git add + git commit + git push
echo.
pause
