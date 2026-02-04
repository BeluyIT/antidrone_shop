#!/usr/bin/env python3
"""Test Telegram API connection."""
import asyncio
import socket
import ssl
import urllib.request

# Test 1: DNS resolution
print("=" * 50)
print("Test 1: DNS Resolution")
print("=" * 50)
try:
    ip = socket.gethostbyname("api.telegram.org")
    print(f"OK: api.telegram.org -> {ip}")
except Exception as e:
    print(f"FAIL: {e}")

# Test 2: HTTPS connection
print("\n" + "=" * 50)
print("Test 2: HTTPS Connection")
print("=" * 50)
try:
    context = ssl.create_default_context()
    with urllib.request.urlopen("https://api.telegram.org", timeout=10, context=context) as response:
        print(f"OK: Status {response.status}")
except Exception as e:
    print(f"FAIL: {e}")

# Test 3: Bot token validation
print("\n" + "=" * 50)
print("Test 3: Bot Token Validation")
print("=" * 50)
try:
    from config import BOT_TOKEN
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    with urllib.request.urlopen(url, timeout=10) as response:
        data = response.read().decode()
        print(f"OK: {data[:100]}...")
except Exception as e:
    print(f"FAIL: {e}")

# Test 4: python-telegram-bot import
print("\n" + "=" * 50)
print("Test 4: Library Import")
print("=" * 50)
try:
    from telegram import __version__
    print(f"OK: python-telegram-bot version {__version__}")
except Exception as e:
    print(f"FAIL: {e}")

# Test 5: Async bot connection
print("\n" + "=" * 50)
print("Test 5: Async Bot Connection")
print("=" * 50)

async def test_bot():
    try:
        from telegram import Bot
        from config import BOT_TOKEN
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        print(f"OK: Bot @{me.username} (ID: {me.id})")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

asyncio.run(test_bot())

print("\n" + "=" * 50)
print("Tests completed!")
print("=" * 50)
