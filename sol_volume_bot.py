import requests
import asyncio
import json
import time
from telegram import Bot
from datetime import datetime

# === CONFIG ===
TOKEN = "7899515001:AAFSWLq3fB4TsrUuLGcyYb1zNG8zyOzy5lg"
CHAT_ID = "5142600981"
VOLUME_MULTIPLIER = 2
CHECK_INTERVAL = 600  # 10 minutes
CHAIN = "solana"
TRACKED_FILE = "tracked_pairs.json"
LIQUIDITY_THRESHOLD = 5000
MIN_VOLUME = 10000
MAX_VOLUME = 100000

bot = Bot(token=TOKEN)

try:
    with open(TRACKED_FILE, 'r') as f:
        tracked_pairs = json.load(f)
except FileNotFoundError:
    tracked_pairs = {}

def save_tracked_pairs():
    with open(TRACKED_FILE, 'w') as f:
        json.dump(tracked_pairs, f, indent=2)

def get_new_solana_pairs():
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=recent"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("❌ Error fetching new pairs:", e, flush=True)
        return []

def is_contract_safe(attributes):
    contract = attributes.get("base_token", {})
    name = contract.get("name", "").lower()
    symbol = contract.get("symbol", "").lower()

    if any(bad in name or bad in symbol for bad in ["mint", "blacklist", "tax", "fee", "trap"]):
        return False

    return True

def get_volume_and_liquidity(pair_id):
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{pair_id}"
    try:
        response = requests.get(url)
        data = response.json()
        attr = data["data"]["attributes"]
        volume = float(attr["volume_usd"]["h24"])
        liquidity = float(attr["reserve_in_usd"])
        verified = attr["base_token"].get("is_verified", False)
        return volume, liquidity, verified
    except Exception as e:
        print(f"❌ Error fetching pair data for {pair_id}: {e}", flush=True)
        return 0.0, 0.0, False

async def monitor():
    await bot.send_message(chat_id=CHAT_ID, text="✅ Test Alert Success!\n\nTelegram bot is working.\nTracking Solana pairs now...")
    print("🚀 10x Potential Detector Bot Started (Solana)...", flush=True)
    while True:
        new_pairs = get_new_solana_pairs()

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                continue  # Skip low liquidity
            if not verified:
                continue  # Skip unverified
            if not is_contract_safe(attributes):
                continue  # Skip unsafe contracts
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                continue  # Skip if volume is not in desired range

            tracked_pairs[pair_id] = {
                "name": name,
                "initial_volume": volume_24h,
                "url": url,
                "alerted": False,
                "added_at": int(time.time())
            }
            print(f"📌 Tracking: {name} | Vol: ${volume_24h:.2f} | Liq: ${liquidity:.2f}", flush=True)

        for pair_id, info in tracked_pairs.items():
            if info["alerted"]:
                continue

            current_volume, _, _ = get_volume_and_liquidity(pair_id)
            if current_volume >= info["initial_volume"] * VOLUME_MULTIPLIER:
                message = (
                    f"🚀 *10x Candidate Alert!*\\n\\n"
                    f"*Pair:* {info['name']}\\n"
                    f"*Initial 24h Volume:* ${info['initial_volume']:,.2f}\\n"
                    f"*Now:* ${current_volume:,.2f}\\n"
                    f"[View on GeckoTerminal]({info['url']})"
                )
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)
                info["alerted"] = True
                print(f"✅ Alert sent for {info['name']}", flush=True)

        save_tracked_pairs()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor())
import asyncio
import json
import time
from telegram import Bot
from datetime import datetime

# === CONFIG ===
TOKEN = "7899515001:AAFSWLq3fB4TsrUuLGcyYb1zNG8zyOzy5lg"
CHAT_ID = "5142600981"
VOLUME_MULTIPLIER = 2
CHECK_INTERVAL = 600  # 10 minutes
CHAIN = "solana"
TRACKED_FILE = "tracked_pairs.json"
LIQUIDITY_THRESHOLD = 5000
MIN_VOLUME = 10000
MAX_VOLUME = 100000

bot = Bot(token=TOKEN)

# Load tracked pairs or start fresh
try:
    with open(TRACKED_FILE, 'r') as f:
        tracked_pairs = json.load(f)
except FileNotFoundError:
    tracked_pairs = {}

def save_tracked_pairs():
    with open(TRACKED_FILE, 'w') as f:
        json.dump(tracked_pairs, f, indent=2)

def get_new_solana_pairs():
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=recent"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("Error fetching new pairs:", e)
        return []

def is_contract_safe(attributes):
    contract = attributes.get("base_token", {})
    name = contract.get("name", "").lower()
    symbol = contract.get("symbol", "").lower()

    if any(bad in name or bad in symbol for bad in ["mint", "blacklist", "tax", "fee", "trap"]):
        return False

    return True

def get_volume_and_liquidity(pair_id):
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{pair_id}"
    try:
        response = requests.get(url)
        data = response.json()
        attr = data["data"]["attributes"]
        volume = float(attr["volume_usd"]["h24"])
        liquidity = float(attr["reserve_in_usd"])
        verified = attr["base_token"].get("is_verified", False)
        return volume, liquidity, verified
    except Exception as e:
        print(f"Error fetching pair data for {pair_id}: {e}")
        return 0.0, 0.0, False

async def monitor():
    await bot.send_message(chat_id=CHAT_ID, text="✅ Test Alert Success!\n\nTelegram bot is working.\nTracking Solana pairs now...")
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                continue  # Skip low liquidity
            if not verified:
                continue  # Skip unverified
            if not is_contract_safe(attributes):
                continue  # Skip unsafe contracts
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                continue  # Skip if volume is not in desired range

            tracked_pairs[pair_id] = {
                "name": name,
                "initial_volume": volume_24h,
                "url": url,
                "alerted": False,
                "added_at": int(time.time())
            }
            print(f"📌 Tracking: {name} | Vol: ${volume_24h:.2f} | Liq: ${liquidity:.2f}")

        for pair_id, info in tracked_pairs.items():
            if info["alerted"]:
                continue

            current_volume, _, _ = get_volume_and_liquidity(pair_id)
            initial_volume = info["initial_volume"]

            if initial_volume == 0:
                continue

            if current_volume >= initial_volume * VOLUME_MULTIPLIER:
                message = (
                    f"🚀 *10x Candidate Alert!*\n\n"
                    f"*Pair:* {info['name']}\n"
                    f"*Initial 24h Volume:* ${initial_volume:,.2f}\n"
                    f"*Now:* ${current_volume:,.2f}\n"
                    f"[View on GeckoTerminal]({info['url']})"
                )
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)
                info["alerted"] = True
                print(f"✅ Alert sent for {info['name']}")

        save_tracked_pairs()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor())
