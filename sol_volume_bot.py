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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("data", [])
        print(f"✅ Fetched {len(pairs)} pools from GeckoTerminal")
        return pairs
    except Exception as e:
        print("❌ Error fetching new pairs:", e)
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
        print(f"❌ Error fetching pair data for {pair_id}: {e}")
        return 0.0, 0.0, False

async def monitor():
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        if not new_pairs:
            print("⚠️ No pairs returned by API.")
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            print(f"🕵️ Found: {name}")

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                print(f"⛔ Skipped {name}: Low liquidity (${liquidity:.2f})")
                continue
            if not verified:
                print(f"⛔ Skipped {name}: Not verified")
                continue
            if not is_contract_safe(attributes):
                print(f"⛔ Skipped {name}: Unsafe contract")
                continue
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                print(f"⛔ Skipped {name}: Volume ${volume_24h:.2f} out of range")
                continue

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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=volume_usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("data", [])
        print(f"✅ Fetched {len(pairs)} active pairs from GeckoTerminal")
        return pairs
    except Exception as e:
        print("❌ Error fetching new pairs:", e)
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
        print(f"❌ Error fetching pair data for {pair_id}: {e}")
        return 0.0, 0.0, False

async def monitor():
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        if not new_pairs:
            print("⚠️ No pairs returned by API.")
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            print(f"🕵️ Found: {name}")

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                print(f"⛔ Skipped {name}: Low liquidity (${liquidity:.2f})")
                continue
            if not verified:
                print(f"⛔ Skipped {name}: Not verified")
                continue
            if not is_contract_safe(attributes):
                print(f"⛔ Skipped {name}: Unsafe contract")
                continue
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                print(f"⛔ Skipped {name}: Volume ${volume_24h:.2f} out of range")
                continue

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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("data", [])
        print(f"✅ Fetched {len(pairs)} new pairs from GeckoTerminal")
        return pairs
    except Exception as e:
        print("❌ Error fetching new pairs:", e)
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
        print(f"❌ Error fetching pair data for {pair_id}: {e}")
        return 0.0, 0.0, False

async def monitor():
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        if not new_pairs:
            print("⚠️ No new pairs found from API.")
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            print(f"🕵️ Found: {name}")

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                print(f"⛔ Skipped {name}: Low liquidity (${liquidity:.2f})")
                continue
            if not verified:
                print(f"⛔ Skipped {name}: Not verified")
                continue
            if not is_contract_safe(attributes):
                print(f"⛔ Skipped {name}: Unsafe contract")
                continue
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                print(f"⛔ Skipped {name}: Volume ${volume_24h:.2f} out of range")
                continue

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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
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
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            print(f"🕵️ Found: {name}")  # Debug print to confirm scanning

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                continue
            if not verified:
                continue
            if not is_contract_safe(attributes):
                continue
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                continue

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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
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
    print("🚀 10x Potential Detector Bot Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            print(f"🕵️ Found: {name}")  # Debug print to confirm scanning

            if pair_id in tracked_pairs:
                continue

            volume_24h, liquidity, verified = get_volume_and_liquidity(pair_id)

            if liquidity < LIQUIDITY_THRESHOLD:
                continue
            if not verified:
                continue
            if not is_contract_safe(attributes):
                continue
            if not (MIN_VOLUME <= volume_24h <= MAX_VOLUME):
                continue

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
LIQUIDITY_THRESHOLD = 100
MIN_VOLUME = 10
MAX_VOLUME = 1000000

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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
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
                continue  # Skip risky contracts

            tracked_pairs[pair_id] = {
                "name": name,
                "initial_volume": volume_24h,
                "url": url,
                "alerted": False,
                "added_at": int(time.time())
            }
            print(f"📌 Tracking: {name} | Vol: ${volume_24h:.2f} | Liq: ${liquidity:.2f}")

        # Check for 2x volume alert
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
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1&sort=created_at"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("Error fetching new pairs:", e)
        return []

def get_volume_24h(pair_id):
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{pair_id}"
    try:
        response = requests.get(url)
        data = response.json()
        volume = float(data["data"]["attributes"]["volume_usd"]["h24"])
        return volume
    except Exception as e:
        print(f"Error fetching volume for {pair_id}:", e)
        return 0.0

async def monitor():
    print("🚀 New Pair Volume Monitor Started (Solana)...")
    while True:
        new_pairs = get_new_solana_pairs()

        for pair in new_pairs:
            pair_id = pair["id"]
            attributes = pair["attributes"]
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"
            volume_24h = float(attributes["volume_usd"]["h24"])

            # If pair not tracked yet, store initial volume
            if pair_id not in tracked_pairs:
                tracked_pairs[pair_id] = {
                    "name": name,
                    "initial_volume": volume_24h,
                    "url": url,
                    "alerted": False,
                    "added_at": int(time.time())
                }
                print(f"📌 Tracking new pair: {name} | Volume: ${volume_24h:.2f}")

        # Check tracked pairs for 2x volume
        for pair_id, info in tracked_pairs.items():
            if info["alerted"]:
                continue  # Already alerted

            current_volume = get_volume_24h(pair_id)
            initial_volume = info["initial_volume"]

            if initial_volume == 0:
                continue  # Skip if no baseline

            if current_volume >= initial_volume * VOLUME_MULTIPLIER:
                message = (
                    f"🚀 *2x Volume Alert!*\n\n"
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

