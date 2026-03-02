@echo off
setlocal enabledelayedexpansion
title Subir a GitHub

echo ========================================
echo   SUBIR PROYECTO A GITHUB
echo ========================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no esta instalado
    pause
    exit /b 1
)

if not exist ".git" (
    echo Inicializando repositorio...
    git init
    echo.
)

if not exist ".gitignore" (
    (
        echo __pycache__/
        echo *.pyc
        echo *.spec
        echo build/
        echo dist/
        echo screenshots/
        echo config_mascota.json
        echo tutorial_visto.flag
        echo *.rar
        echo *.zip
    ) > .gitignore
)

echo Agregando archivos...
git add .

set /p mensaje=Mensaje del commit: 
if "!mensaje!"=="" set mensaje=Actualizacion

echo Haciendo commit...
git commit -m "!mensaje!"
echo.

git remote -v | findstr origin >nul 2>&1
if errorlevel 1 (
    echo.
    set /p repo_url=URL del repositorio: 
    
    if not "!repo_url!"=="" (
        echo Agregando repositorio remoto...
        git remote add origin !repo_url!
    ) else (
        echo ERROR: URL vacia
        pause
        exit /b 1
    )
)

git branch -M main

echo.
echo Subiendo a GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo El repo remoto tiene archivos. Opciones:
    echo 1. Forzar push (SOBRESCRIBE el remoto)
    echo 2. Hacer pull primero (mezcla cambios)
    echo 3. Cancelar
    echo.
    choice /c 123 /n /m "Elige opcion (1/2/3): "
    
    if errorlevel 3 (
        echo Cancelado
        pause
        exit /b 1
    )
    if errorlevel 2 (
        echo Haciendo pull...
        git pull origin main --allow-unrelated-histories
        echo Intentando push de nuevo...
        git push -u origin main
    )
    if errorlevel 1 (
        echo Forzando push...
        git push -u origin main --force
    )
)

echo.
echo ========================================
echo   SUBIDO EXITOSAMENTE
echo ========================================
pause
