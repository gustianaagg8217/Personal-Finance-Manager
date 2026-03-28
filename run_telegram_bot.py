#!/usr/bin/env python3
"""Launcher for Personal Finance Manager Telegram Bot."""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot import FinanceBot
from telegram.error import Conflict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run Telegram bot."""
    import os
    
    # Get token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("\n❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nSetup:")
        print("1. Create bot with @BotFather on Telegram")
        print("2. Set environment variable:")
        print("   Windows (PowerShell): $env:TELEGRAM_BOT_TOKEN = 'your_token'")
        print("   Windows (CMD): set TELEGRAM_BOT_TOKEN=your_token")
        print("   Linux/Mac: export TELEGRAM_BOT_TOKEN=your_token")
        print("\n3. Run this script again")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("TELEGRAM BOT - PERSONAL FINANCE MANAGER")
    print("=" * 60)
    print("\n🤖 Memulai bot...\n")
    
    try:
        bot = FinanceBot(token)
        bot.run()
    except Conflict as e:
        print(f"\n❌ Bot Instance Conflict: {e}")
        print("\n⚠️  Another bot instance is already running with this token!")
        print("Options:")
        print("   1. Stop other bot instances running in different terminals")
        print("   2. Wait 30-60 seconds and try again (Telegram clears old sessions)")
        print("   3. Use a different token from @BotFather")
        logger.error("Conflict error - multiple instances detected", exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Bot dihentikan oleh user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
