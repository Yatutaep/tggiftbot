import os
import asyncio
import logging
import re
from telegram import Bot
from telegram.error import InvalidToken
from playwright.async_api import async_playwright

# ================== CONFIG ==================

TOKEN = "8790754103:AAGjqIdPbSwlwNwHdPDCDdd_brDJQZCaybc"
CHAT_ID = "5778701701"

MARKETS = ["Portals", "Tonnel", "MRKT"]
CHECK_INTERVAL = 15
MIN_PROFIT_PERCENT = 1

# ============================================
print("TOKEN OK")
print("CHAT_ID =", CHAT_ID)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

if not CHAT_ID:
    raise ValueError("CHAT_ID не найден!")

CHAT_ID = int(CHAT_ID)

try:
    bot = Bot(token=TOKEN)
except InvalidToken:
    raise ValueError("Неверный BOT_TOKEN!")

seen = set()


async def send(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")


def extract_price(text):
    # Ищем первое число в тексте
    numbers = re.findall(r"\d+", text)
    if numbers:
        return int(numbers[0])
    return None


def calculate_profit(gift, floor):
    if not floor:
        return 0
    return ((floor - gift) / floor) * 100


async def monitor():
    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto("https://web.telegram.org")
                await asyncio.sleep(10)

                await send("🚀 PRO мониторинг запущен")
                while True:
                        print("🔍 Проверяю рынок...")
                        await asyncio.sleep(10)
                

                while True:
                    content = await page.content()

                    for market in MARKETS:

                        if market in content:

                            gift_price = extract_price(content)
                            floor_price = gift_price + 5  # Заглушка анализа

                            profit = calculate_profit(gift_price, floor_price)

                            if profit >= MIN_PROFIT_PERCENT:

                                item_id = f"{market}-{gift_price}"

                                if item_id not in seen:

                                    await send(
                                        f"🔥 PRO ЛОТ\n"
                                        f"Маркет: {market}\n"
                                        f"Цена: {gift_price} TON\n"
                                        f"Floor: {floor_price} TON\n"
                                        f"📊 Выгода: {profit:.2f}%"
                                    )
     
                                    seen.add(item_id)

                    await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logging.error(f"Ошибка системы: {e}")
            await asyncio.sleep(10)


async def main():
    await monitor()


if __name__ == "__main__":
    asyncio.run(main())
