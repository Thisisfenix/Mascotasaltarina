@echo off
echo Limpiando HolaGissel.rar del historial...
echo.

git rm --cached HolaGissel.rar
git commit -m "Eliminar archivo .rar grande"

echo.
echo Listo! Ahora ejecuta subir_repo.bat
pause
