@echo off
echo ========================================
echo   COMPILANDO A EJECUTABLE (.EXE)
echo ========================================
echo.

REM Instalar PyInstaller si no está instalado
echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo Compilando mascota_saltarina.py a EXE...
echo.

REM Limpiar compilaciones anteriores
if exist build rmdir /s /q build
if exist HolaGissel rmdir /s /q HolaGissel
if exist MascotaSaltarina.spec del MascotaSaltarina.spec

REM Compilar con icono personalizado usando python -m
python -m PyInstaller --onefile --windowed --icon="%cd%\assets\icon.ico" --name="MascotaSaltarina" --distpath="HolaGissel" mascota_saltarina.py

echo.
echo Copiando carpeta assets...
xcopy /E /I /Y assets HolaGissel\assets

echo.
echo Copiando carpeta mods...
if exist mods (
    xcopy /E /I /Y mods HolaGissel\mods
    echo Carpeta mods copiada!
) else (
    mkdir HolaGissel\mods
    echo Carpeta mods creada (vacia)
)

echo.
echo Copiando icono junto al ejecutable...
if exist assets\icon.ico (
    copy assets\icon.ico HolaGissel\icon.ico
    echo Icono copiado!
)

echo.
echo Copiando carpeta de videos si existe...
if exist assets\video (
    xcopy /E /I /Y assets\video HolaGissel\assets\video
    echo Carpeta de videos copiada!
) else (
    echo No se encontro carpeta de videos (opcional)
)

echo.
echo ========================================
echo   COMPILACION COMPLETADA
echo ========================================
echo.
echo El ejecutable esta listo en: HolaGissel\MascotaSaltarina.exe
echo La carpeta assets ya fue copiada automaticamente.
echo La carpeta mods ya fue copiada automaticamente.
echo.
echo NOTA: Los usuarios pueden agregar archivos .py en la carpeta mods/
echo para instalar mods personalizados!
echo.
pause
