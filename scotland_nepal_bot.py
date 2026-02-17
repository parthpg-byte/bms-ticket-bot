from playwright.sync_api import sync_playwright
import time
import requests
import re

EVENT_URL = "https://in.bookmyshow.com/sports/scotland-vs-nepal-icc-men-s-t20-wc-2026/ET00483432"

BOT_TOKEN = "8217148577:AAH0pyQPe0ZyBxuTERi-5IPoK-iEGfjhvho"
CHAT_ID = "7577106202"

last_price = None


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


def extract_prices(text):
    prices = re.findall(r'₹\s?(\d+)', text)
    return [int(p) for p in prices]


def check_tickets():
    global last_price

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Checking ticket prices...")
        page.goto(EVENT_URL, timeout=60000)
        page.wait_for_timeout(5000)

        text = page.inner_text("body")
        prices = extract_prices(text)

        if prices:
            current_min_price = min(prices)
            print("Current lowest price:", current_min_price)

            if last_price is None:
                last_price = current_min_price
                send_telegram(
                    f"🎟 Scotland vs Nepal\nCurrent lowest price: ₹{current_min_price}"
                )

            elif current_min_price != last_price:
                send_telegram(
                    f"🚨 Price changed!\nOld: ₹{last_price}\nNew: ₹{current_min_price}\n{EVENT_URL}"
                )
                last_price = current_min_price
        else:
            print("No prices detected.")

        browser.close()


while True:
    check_tickets()
    time.sleep(120)  # check every 2 minutes
