@echo off
REM Personal Finance Manager - Quick Launcher
REM This batch file provides easy access to start the application

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ===== ERROR =====
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

REM Display menu
:menu
cls
color 0B
echo.
echo ============================================
echo   PERSONAL FINANCE MANAGER
echo   💰 Launcher Menu
echo ============================================
echo.
echo   1) Start CLI Application
echo   2) Start Telegram Bot
echo   3) Start Both (CLI + Bot)
echo   4) Stop All Running Processes
echo   5) View Documentation
echo   0) Exit
echo.
echo ============================================
echo.
set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto start_cli
if "%choice%"=="2" goto start_bot
if "%choice%"=="3" goto start_both
if "%choice%"=="4" goto stop_all
if "%choice%"=="5" goto docs
if "%choice%"=="0" exit /b 0
echo Invalid choice! Press any key to try again.
pause
goto menu

:start_cli
echo.
echo 🚀 Starting CLI Application...
echo.
start python main.py
timeout /t 2 /nobreak
goto menu

:start_bot
echo.
echo 🤖 Starting Telegram Bot...
echo.

REM Check if TELEGRAM_BOT_TOKEN is set
if not defined TELEGRAM_BOT_TOKEN (
    color 0C
    cls
    echo.
    echo ============================================
    echo   ⚠️  ERROR: Telegram Bot Token Not Found
    echo ============================================
    echo.
    echo TELEGRAM_BOT_TOKEN environment variable is not set!
    echo.
    echo SOLUTION:
    echo -----------
    echo 1. Go to https://t.me/BotFather on Telegram
    echo 2. Create a new bot and copy the TOKEN
    echo 3. Choose an option below:
    echo.
    echo   A) Set token for THIS session only
    echo   B) Set token permanently (System Environment)
    echo   C) Cancel
    echo.
    echo ============================================
    echo.
    set /p token_choice="Enter your choice (A/B/C): "
    
    if /i "%token_choice%"=="A" (
        set /p token_input="Enter your Telegram Bot Token: "
        set TELEGRAM_BOT_TOKEN=!token_input!
        echo.
        echo ✅ Token set for this session
        echo.
        goto start_bot
    )
    if /i "%token_choice%"=="B" (
        set /p token_input="Enter your Telegram Bot Token: "
        setx TELEGRAM_BOT_TOKEN "!token_input!"
        echo.
        echo ✅ Token saved to system environment
        echo   (You may need to restart your terminal)
        echo.
        set TELEGRAM_BOT_TOKEN=!token_input!
        timeout /t 2 /nobreak
        goto start_bot
    )
    if /i "%token_choice%"=="C" (
        goto menu
    )
)

REM Start bot in new window with error output visible
echo Launching bot in new window...
echo.
start "Personal Finance Manager - Telegram Bot" python run_telegram_bot.py

REM Check if process started successfully
timeout /t 3 /nobreak
tasklist | find "python.exe" >nul
if errorlevel 1 (
    color 0C
    cls
    echo.
    echo ============================================
    echo   ⚠️  ERROR: Bot failed to start
    echo ============================================
    echo.
    echo Possible reasons:
    echo 1. Invalid Telegram Bot Token
    echo 2. Missing dependencies (python-telegram-bot)
    echo 3. Network connection issue
    echo.
    echo Try running manually for detailed error:
    echo   python run_telegram_bot.py
    echo.
    echo ============================================
    echo.
    pause
) else (
    color 0A
    echo.
    echo ✅ Telegram Bot started successfully!
    echo.
    echo Bot commands available:
    echo   /add_transaction  - Add transaction
    echo   /summary          - View summary
    echo   /analytics        - Financial health
    echo   /help             - Show all commands
    echo.
    echo Close this window to stop the bot.
    echo.
    timeout /t 5 /nobreak
)

goto menu

:start_both
echo.
echo 🚀 Starting CLI Application...
start python main.py
echo 🤖 Starting Telegram Bot...
start python run_telegram_bot.py
echo.
echo Both applications started!
timeout /t 3 /nobreak
goto menu

:stop_all
echo.
echo ⏹ Stopping all Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
echo Done!
timeout /t 2 /nobreak
goto menu

:docs
echo.
echo 📖 Opening documentation...
if exist README.md (
    start README.md
) else (
    echo README.md not found!
)
timeout /t 2 /nobreak
goto menu
