@echo off
echo ========================================
echo   COMPILANDO A EJECUTABLE (.EXE)
echo ========================================
echo.

REM Instalar PyInstaller si no está instalado
echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo ========================================
echo   COMPILANDO MASCOTA SALTARINA
echo ========================================
echo.

REM Limpiar compilaciones anteriores Y CACHE
echo Limpiando cache y archivos antiguos...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist mascota_saltarina.spec del mascota_saltarina.spec
if exist MascotaSaltarina.spec del MascotaSaltarina.spec

REM Limpiar cache de PyInstaller (IMPORTANTE para evitar usar codigo viejo)
if exist "%LOCALAPPDATA%\pyinstaller" rmdir /s /q "%LOCALAPPDATA%\pyinstaller"
if exist "%TEMP%\pyinstaller" rmdir /s /q "%TEMP%\pyinstaller"

REM Generar spec file con compresión UPX
echo Generando spec file optimizado con UPX...
python -m PyInstaller --onefile --windowed --icon="%cd%\assets\icon.ico" --name="MascotaSaltarina" --hidden-import=psutil --hidden-import=pycaw --hidden-import=comtypes --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module numpy.testing --exclude-module setuptools --exclude-module distutils --exclude-module test --exclude-module unittest mascota_saltarina.py

REM Modificar spec para habilitar UPX
echo Habilitando compresión UPX en spec file...
powershell -Command "(Get-Content MascotaSaltarina.spec) -replace 'upx=False', 'upx=True' | Set-Content MascotaSaltarina.spec"

REM Compilar usando el spec modificado
echo Compilando con UPX...
python -m PyInstaller MascotaSaltarina.spec

echo.
echo Moviendo ejecutable a HolaGissel...
if not exist HolaGissel mkdir HolaGissel
move /Y dist\MascotaSaltarina.exe HolaGissel\MascotaSaltarina.exe

echo.
echo Copiando carpeta assets...
xcopy /E /I /Y assets HolaGissel\assets

echo.
echo Copiando icon.ico...
if exist icon.ico copy /Y icon.ico HolaGissel\icon.ico
if exist assets\icon.ico copy /Y assets\icon.ico HolaGissel\icon.ico

echo.
echo Copiando carpeta mods...
if exist mods (
    xcopy /E /I /Y mods HolaGissel\mods
) else (
    if not exist HolaGissel\mods mkdir HolaGissel\mods
)

echo.
echo Copiando carpeta dlc...
if exist dlc (
    xcopy /E /I /Y dlc HolaGissel\dlc
    echo DLCs copiados
) else (
    if not exist HolaGissel\dlc mkdir HolaGissel\dlc
    echo Carpeta dlc creada
)

echo.
echo Copiando version.txt...
if exist version.txt (
    copy /Y version.txt HolaGissel\version.txt
    echo version.txt copiado
) else (
    echo 2.0.0 > HolaGissel\version.txt
    echo version.txt creado con version 2.0.0
)



echo.
echo Limpiando archivos temporales...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist MascotaSaltarina.spec del MascotaSaltarina.spec
if exist mascota_saltarina.spec del mascota_saltarina.spec

echo.
echo ========================================
echo   COMPILACION COMPLETADA
echo ========================================
echo.
echo Ejecutable: HolaGissel\MascotaSaltarina.exe
echo Assets: HolaGissel\assets\
echo Mods: HolaGissel\mods\
echo DLCs: HolaGissel\dlc\
echo Version: HolaGissel\version.txt
echo.
echo IMPORTANTE: Actualiza HolaGissel\version.txt antes de subir!
echo.
pause
