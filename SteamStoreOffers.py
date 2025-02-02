import asyncio
import requests
import json
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "7275053664:AAFqQljTHEcIfwOUWjv0C4W_c3v4qpvy6-Y"
CHAT_ID = "@SteamStoreOffers"
DATA_FILE = "sent_games.json"

# Fetch Steam discounts
def get_steam_discounts():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        discounted_games = []
        seen_ids = set()

        for category in data.get("specials", {}).get("items", []):
            game_id = str(category.get("id"))
            if game_id in seen_ids:
                print("Checked")
                continue

            seen_ids.add(game_id)

            name = category.get("name", "No Name")
            original_price = category.get("original_price", 0) / 100
            final_price = category.get("final_price", 0) / 100
            discount_percent = category.get("discount_percent", 0)
            steam_url = f"https://store.steampowered.com/app/{game_id}/"

            if discount_percent >= 50 or final_price == 0:
                discounted_games.append({
                    "id": game_id,
                    "name": name,
                    "original_price": round(original_price, 2),
                    "final_price": round(final_price, 2),
                    "discount_percent": discount_percent,
                    "steam_url": steam_url
                })

        return discounted_games
    return []

# Load sent games
def load_sent_games():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save sent games
def save_sent_games(sent_games):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sent_games, f, indent=4, ensure_ascii=False)

# Send Telegram message with button
async def send_telegram_message(text, url):
    bot = Bot(token=TOKEN)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 View on Steam", url=url)]])
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML", reply_markup=keyboard)

# Main function
async def main():
    sent_games = load_sent_games()
    sent_game_ids = {game["id"] for game in sent_games}

    while True:
        games = get_steam_discounts()
        new_games = [game for game in games if game["id"] not in sent_game_ids]

        if new_games:
            for game in new_games:
                message = f"""
🎮 <b>{game['name']}</b>

💰 Original Price: {game['original_price']}$ 
🔥 Discounted Price: {game['final_price']}$ (-{game['discount_percent']}%)

🔗 <a href="{game['steam_url']}">Steam Link</a>
"""
                await send_telegram_message(message, game["steam_url"])
                sent_games.append(game)
                sent_game_ids.add(game["id"])

            save_sent_games(sent_games)

        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
