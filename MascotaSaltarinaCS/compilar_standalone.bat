@echo off
echo ========================================
echo   Compilando Ankush Cat (Standalone)
echo ========================================
echo.
echo Este proceso puede tardar varios minutos...
echo Se creara un ejecutable que NO requiere .NET instalado
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

echo [1/4] Restaurando paquetes NuGet...
dotnet restore
if %errorlevel% neq 0 (
    echo ERROR: Fallo al restaurar paquetes
    pause
    exit /b 1
)

echo.
echo [2/4] Compilando proyecto...
dotnet build --configuration Release
if %errorlevel% neq 0 (
    echo ERROR: Fallo al compilar
    pause
    exit /b 1
)

echo.
echo [3/4] Publicando ejecutable standalone (esto puede tardar)...
dotnet publish --configuration Release --output ./publish-standalone --self-contained true --runtime win-x64 /p:PublishSingleFile=true /p:IncludeNativeLibrariesForSelfExtract=true
if %errorlevel% neq 0 (
    echo ERROR: Fallo al publicar
    pause
    exit /b 1
)

echo.
echo [4/4] Copiando assets...
xcopy /E /I /Y assets publish-standalone\assets >nul 2>&1
copy /Y version.txt publish-standalone\ >nul 2>&1
copy /Y icon.ico publish-standalone\ >nul 2>&1

echo.
echo ========================================
echo   Compilacion exitosa!
echo ========================================
echo.
echo El ejecutable standalone se encuentra en:
echo ./publish-standalone/AnkushCat.exe
echo.
echo Este ejecutable incluye todo lo necesario y puede
echo ejecutarse en cualquier PC con Windows 10/11
echo sin necesidad de instalar .NET
echo.
pause
