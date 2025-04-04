import requests
import asyncio
import json
import time
from telegram import Bot

# === CONFIG ===
TOKEN = "7899515001:AAFSWLq3fB4TsrUuLGcyYb1zNG8zyOzy5lg"
CHAT_ID = "5142600981"
CHAIN = "solana"
CHECK_INTERVAL = 60  # Check every 60 seconds
TX_ENDPOINT = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1"
MIN_BUY_USD = 1000
ALERTED_TX_FILE = "alerted_whale_txs.json"

bot = Bot(token=TOKEN)

# Load already-alerted txs
try:
    with open(ALERTED_TX_FILE, 'r') as f:
        alerted_txs = json.load(f)
except FileNotFoundError:
    alerted_txs = []

def save_alerted_txs():
    with open(ALERTED_TX_FILE, 'w') as f:
        json.dump(alerted_txs, f)

def get_recent_pools():
    try:
        response = requests.get(TX_ENDPOINT)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except Exception as e:
        print("❌ Error fetching pool list:", e)
        return []

def get_recent_transactions(pair_id):
    try:
        # Remove 'solana_' prefix to get correct GeckoTerminal pool address
        pool_address = pair_id.split("_")[-1]
        url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{pool_address}/swaps"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except Exception as e:
        print(f"❌ Error fetching transactions for {pair_id}: {e}")
        return []

async def check_whale_buys():
    print("🐳 Whale Alert Bot running...")
    while True:
        pools = get_recent_pools()

        for pool in pools:
            pair_id = pool.get("id")
            attributes = pool.get("attributes", {})
            name = attributes.get("name", "Unknown")
            pool_address = pair_id.split("_")[-1]
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pool_address}"

            txs = get_recent_transactions(pair_id)
            for tx in txs:
                tx_id = tx.get("id")
                if tx_id in alerted_txs:
                    continue

                tx_attrs = tx.get("attributes", {})
                tx_type = tx_attrs.get("trade_type")
                usd_value = float(tx_attrs.get("value_usd", 0))

                if tx_type == "buy" and usd_value >= MIN_BUY_USD:
                    message = (
                        f"🐳 *Whale Buy Detected!*\n\n"
                        f"*Token:* {name}\n"
                        f"*Amount:* ${usd_value:,.2f}\n"
                        f"[View on GeckoTerminal]({url})"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)
                    print(f"✅ Alert sent: {name} ${usd_value}")
                    alerted_txs.append(tx_id)

        save_alerted_txs()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(check_whale_buys())
import requests
import asyncio
import json
import time
from telegram import Bot

# === CONFIG ===
TOKEN = "7899515001:AAFSWLq3fB4TsrUuLGcyYb1zNG8zyOzy5lg"
CHAT_ID = "5142600981"
CHAIN = "solana"
CHECK_INTERVAL = 60  # Check every 60 seconds
TX_ENDPOINT = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools?page=1"
MIN_BUY_USD = 1000
ALERTED_TX_FILE = "alerted_whale_txs.json"

bot = Bot(token=TOKEN)

# Load already-alerted txs
try:
    with open(ALERTED_TX_FILE, 'r') as f:
        alerted_txs = json.load(f)
except FileNotFoundError:
    alerted_txs = []

def save_alerted_txs():
    with open(ALERTED_TX_FILE, 'w') as f:
        json.dump(alerted_txs, f)

def get_recent_pools():
    try:
        response = requests.get(TX_ENDPOINT)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except Exception as e:
        print("❌ Error fetching pool list:", e)
        return []

def get_recent_transactions(pair_id):
    url = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{pair_id}/swaps"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except Exception as e:
        print(f"❌ Error fetching transactions for {pair_id}:", e)
        return []

async def check_whale_buys():
    print("🐳 Whale Alert Bot running...")
    while True:
        pools = get_recent_pools()

        for pool in pools:
            pair_id = pool.get("id")
            attributes = pool.get("attributes", {})
            name = attributes.get("name", "Unknown")
            url = f"https://www.geckoterminal.com/{CHAIN}/pools/{pair_id.split('/')[-1]}"

            txs = get_recent_transactions(pair_id)
            for tx in txs:
                tx_id = tx.get("id")
                if tx_id in alerted_txs:
                    continue

                tx_attrs = tx.get("attributes", {})
                tx_type = tx_attrs.get("trade_type")
                usd_value = float(tx_attrs.get("value_usd", 0))

                if tx_type == "buy" and usd_value >= MIN_BUY_USD:
                    message = (
                        f"🐳 *Whale Buy Detected!*\n\n"
                        f"*Token:* {name}\n"
                        f"*Amount:* ${usd_value:,.2f}\n"
                        f"[View on GeckoTerminal]({url})"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)
                    print(f"✅ Alert sent: {name} ${usd_value}")
                    alerted_txs.append(tx_id)

        save_alerted_txs()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(check_whale_buys())

