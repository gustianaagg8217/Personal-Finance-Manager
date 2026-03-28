@echo off
REM Personal Finance Manager - Telegram Bot Setup
REM Interactive setup for TELEGRAM_BOT_TOKEN

setlocal enabledelayedexpansion

cls
color 0B
echo.
echo ============================================
echo   TELEGRAM BOT SETUP
echo   Personal Finance Manager
echo ============================================
echo.
echo This script will help you configure your
echo Telegram Bot Token for the Finance Manager.
echo.
echo ============================================
echo.

REM Check if token already exists
if defined TELEGRAM_BOT_TOKEN (
    echo Current token (hidden): [SET]
    echo.
)

:choose_method
cls
echo.
echo ============================================
echo   SETUP METHOD
echo ============================================
echo.
echo Choose how to set your Telegram Bot Token:
echo.
echo   1) Automatic Setup (Recommended)
echo      - Create bot with @BotFather
echo      - Token saved to system environment
echo.
echo   2) Manual Setup
echo      - Enter token manually
echo      - Saved for this session only
echo.
echo   3) Test Current Token
echo      - Verify if current token works
echo.
echo   4) Clear Saved Token
echo      - Remove token from system environment
echo.
echo   0) Exit
echo.
echo ============================================
echo.
set /p method="Enter your choice (0-4): "

if "%method%"=="1" goto auto_setup
if "%method%"=="2" goto manual_setup
if "%method%"=="3" goto test_token
if "%method%"=="4" goto clear_token
if "%method%"=="0" exit /b 0

echo Invalid choice! Press any key to try again.
pause
goto choose_method

:auto_setup
cls
echo.
echo ============================================
echo   STEP 1: Create Bot with BotFather
echo ============================================
echo.
echo 1. Open Telegram and search for: @BotFather
echo 2. Send command: /newbot
echo 3. Follow the instructions to create a bot
echo 4. You will receive a token like:
echo    1234567890:ABCDefGHIJKLmnoPQRstUVwxyz_1234567890
echo.
echo ============================================
echo.

set /p token_input="Paste your Telegram Bot Token here: "

if "!token_input!"=="" (
    echo.
    echo ❌ No token provided!
    pause
    goto choose_method
)

echo.
echo Saving token to system environment...
setx TELEGRAM_BOT_TOKEN "!token_input!"

if errorlevel 1 (
    color 0C
    echo.
    echo ❌ Failed to save token to system!
    echo Try running as Administrator.
    echo.
    pause
) else (
    color 0A
    echo.
    echo ✅ Token saved successfully!
    echo.
    echo ⚠️  Please restart your terminal or command prompt
    echo   for the changes to take effect.
    echo.
    set TELEGRAM_BOT_TOKEN=!token_input!
)

pause
goto choose_method

:manual_setup
cls
echo.
echo ============================================
echo   MANUAL SETUP
echo ============================================
echo.
set /p token_input="Enter your Telegram Bot Token: "

if "!token_input!"=="" (
    echo.
    echo ❌ No token provided!
    pause
    goto choose_method
)

set TELEGRAM_BOT_TOKEN=!token_input!
echo.
echo ✅ Token set for this session!
echo.
echo Note: This will only work until you close this window.
echo Run "setup_telegram.bat" again and choose option 1
echo to save it permanently.
echo.
pause
goto choose_method

:test_token
cls
echo.
echo ============================================
echo   TEST TOKEN
echo ============================================
echo.

if not defined TELEGRAM_BOT_TOKEN (
    color 0C
    echo ❌ No token found!
    echo.
    echo Please set a token first (options 1 or 2)
    echo.
) else (
    echo ⏳ Testing token... (connecting to Telegram API)
    echo.
    
    REM Create a temporary Python script to test the token
    (
        echo import os
        echo from telegram import Bot
        echo from telegram.error import TelegramError
        echo.
        echo token = os.getenv("TELEGRAM_BOT_TOKEN"^)
        echo.
        echo if not token:
        echo     print("❌ Token not found in environment"^)
        echo     exit(1
        echo.
        echo try:
        echo     bot = Bot(token=token^)
        echo     me = bot.get_me(^)
        echo     print(f"✅ Token is VALID!"^)
        echo     print(f"   Bot Name: @{me.username}"^)
        echo     print(f"   Bot ID: {me.id}"^)
        echo except TelegramError as e:
        echo     print(f"❌ Token is INVALID or Bot is offline"^)
        echo     print(f"   Error: {e}"^)
        echo     exit(1^)
    ) > test_token.py
    
    python test_token.py
    set exit_code=!errorlevel!
    del test_token.py
    
    echo.
    if !exit_code! equ 0 (
        color 0A
        echo.
        echo You can now start the bot!
    ) else (
        color 0C
        echo.
        echo Please check your token and try again.
    )
)

echo.
pause
goto choose_method

:clear_token
cls
echo.
echo ============================================
echo   CLEAR TOKEN
echo ============================================
echo.
echo This will remove the token from system environment.
echo.

set /p confirm="Are you sure? (Y/N): "

if /i "%confirm%"=="Y" (
    REM Use PowerShell to remove environment variable
    powershell -NoProfile -Command "Remove-Item env:TELEGRAM_BOT_TOKEN -ErrorAction SilentlyContinue" >nul 2>&1
    
    REM Also try to remove from registry
    reg delete "HKCU\Environment" /F /V TELEGRAM_BOT_TOKEN >nul 2>&1
    
    color 0A
    echo.
    echo ✅ Token cleared from system!
    echo.
) else (
    echo.
    echo Cancelled.
    echo.
)

pause
goto choose_method
