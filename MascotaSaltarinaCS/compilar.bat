@echo off
echo ========================================
echo   Compilando Ankush Cat (C# Version)
echo ========================================
echo.

REM Verificar si dotnet está instalado
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: .NET SDK no está instalado
    echo Por favor instala .NET 8.0 o superior desde:
    echo https://dotnet.microsoft.com/download
    pause
    exit /b 1
)

echo [1/3] Restaurando paquetes NuGet...
dotnet restore
if %errorlevel% neq 0 (
    echo ERROR: Fallo al restaurar paquetes
    pause
    exit /b 1
)

echo.
echo [2/3] Compilando proyecto...
dotnet build --configuration Release
if %errorlevel% neq 0 (
    echo ERROR: Fallo al compilar
    pause
    exit /b 1
)

echo.
echo [3/3] Publicando ejecutable...
dotnet publish --configuration Release --output ./publish --self-contained false
if %errorlevel% neq 0 (
    echo ERROR: Fallo al publicar
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Compilacion exitosa!
echo ========================================
echo.
echo El ejecutable se encuentra en: ./publish/AnkushCat.exe
echo.
pause
