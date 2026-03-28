@echo off
REM ============================================
REM Personal Finance Manager
REM Quick Telegram Token Setter
REM ============================================

color 0B
cls
echo.
echo ============================================
echo   QUICK TELEGRAM TOKEN SETUP
echo ============================================
echo.
echo Step 1: Create bot with @BotFather on Telegram
echo         Command: /newbot
echo.
echo Step 2: Copy your bot token
echo         Format: 1234567890:ABCDefGHIJKL...
echo.
echo ============================================
echo.

if defined TELEGRAM_BOT_TOKEN (
    echo Current token is SET: [***HIDDEN***]
    echo Do you want to:
    echo   R) Replace it with new token
    echo   K) Keep existing token and proceed
    echo   C) Cancel
    echo.
    set /p existing="Enter choice (R/K/C): "
    if /i "%existing%"=="C" exit /b 0
    if /i "%existing%"=="K" goto test_and_proceed
)

:enter_token
echo.
set /p TELEGRAM_BOT_TOKEN="Paste your Telegram Bot Token: "

if "!TELEGRAM_BOT_TOKEN!"=="" (
    echo.
    echo ❌ No token entered!
    pause
    exit /b 1
)

echo.
echo ⏳ Saving token to system environment...
echo.

setx TELEGRAM_BOT_TOKEN "!TELEGRAM_BOT_TOKEN!"

if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Could not save token!
    echo.
    echo Try running as Administrator or use:
    echo   set TELEGRAM_BOT_TOKEN=your_token_here
    echo.
) else (
    color 0A
    set TELEGRAM_BOT_TOKEN=!TELEGRAM_BOT_TOKEN!
    goto test_and_proceed
)

pause
exit /b 1

:test_and_proceed
cls
echo.
echo ✅ Token configured!
echo.
echo Next steps:
echo.
echo   1. Start launcher.bat
echo   2. Choose "2) Start Telegram Bot"
echo   3. Bot will start in new window
echo.
echo ============================================
echo.
echo Want to start bot now? (Y/N)
set /p start_now="Enter choice: "

if /i "%start_now%"=="Y" (
    echo.
    echo 🚀 Starting bot...
    echo.
    start "Personal Finance Manager - Telegram Bot" python run_telegram_bot.py
    timeout /t 3
    echo.
    echo ✅ Bot started!
    echo   Check bot window for activity log
    echo.
) else (
    echo.
    echo 📝 Reminder:
    echo   Run "launcher.bat" to start the application
    echo.
)

pause
