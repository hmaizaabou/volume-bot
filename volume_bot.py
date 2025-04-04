import requests
import asyncio
from telegram import Bot

TOKEN = "7899515001:AAFSWLq3fB4TsrUuLGcyYb1zNG8zyOzy5lg"
CHAT_ID = "5142600981"
VOLUME_THRESHOLD = 5000

with open('volume_pairs.txt', 'r') as file:
    pair_urls = [line.strip() for line in file if line.strip()]

bot = Bot(token=TOKEN)

async def fetch_pair_data(pair_url):
    api_url = pair_url.replace('www.geckoterminal.com', 'api.geckoterminal.com/api/v2')
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed for {pair_url}: {e}")
        return None

async def monitor_volume():
    alerted_pairs = set()
    print("🚀 Volume monitoring started...")
    while True:
        for url in pair_urls:
            data = await fetch_pair_data(url)
            if data:
                attributes = data.get('data', {}).get('attributes', {})
                name = attributes.get('name', 'Unknown Pair')
                volume_usd = float(attributes.get('volume_usd', {}).get('h24', 0))

                if volume_usd >= VOLUME_THRESHOLD and url not in alerted_pairs:
                    message = (
                        f"🚨 *Volume Alert!*\n\n"
                        f"*Pair:* {name}\n"
                        f"*24h Volume:* ${volume_usd:,.2f}\n"
                        f"[View Pair]({url})"
                    )
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    alerted_pairs.add(url)
                    print(f"✅ Alert sent for {name} with volume ${volume_usd:.2f}")

        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == '__main__':
    asyncio.run(monitor_volume())

