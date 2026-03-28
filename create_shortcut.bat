@echo off
REM Personal Finance Manager - Desktop Shortcut Creator
REM Creates a shortcut on the desktop for quick access

setlocal enabledelayedexpansion

REM Get current directory
for /f "tokens=*" %%A in ('cd') do set "current_dir=%%A"

REM Get desktop path
for /f "tokens=3" %%A in ('reg query "HKCU\Desktop" /ve 2^>nul') do set "desktop_path=%%A"
if not defined desktop_path (
    set "desktop_path=%USERPROFILE%\Desktop"
)

REM Create shortcut using PowerShell
powershell -NoProfile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%desktop_path%\Personal Finance Manager.lnk'); " ^
    "$Shortcut.TargetPath = 'cmd.exe'; " ^
    "$Shortcut.Arguments = '/c cd /d \"%current_dir%\" ^& python launcher.py'; " ^
    "$Shortcut.WorkingDirectory = '%current_dir%'; " ^
    "$Shortcut.Icon = '%current_dir%\launcher.py'; " ^
    "$Shortcut.Save()"

if errorlevel 0 (
    color 0A
    cls
    echo.
    echo ============================================
    echo   SUCCESS!
    echo ============================================
    echo.
    echo Shortcut created on Desktop:
    echo "Personal Finance Manager.lnk"
    echo.
    echo Double-click to launch the application!
    echo.
) else (
    color 0C
    echo.
    echo Error creating shortcut!
    echo.
)
pause
