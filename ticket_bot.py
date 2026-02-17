from playwright.sync_api import sync_playwright
import time
import requests
import re

EVENT_URL = "https://in.bookmyshow.com/sports/super-8-match-4-icc-men-s-t20-wc-2026/ET00474270"

BOT_TOKEN = "8217148577:AAH0pyQPe0ZyBxuTERi-5IPoK-iEGfjhvho"
CHAT_ID = "7577106202"

last_price = None
last_status_time = 0


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


def extract_price(text):
    match = re.search(r'₹\s?(\d+)', text)
    if match:
        return int(match.group(1))
    return None


def check_tickets():
    global last_price, last_status_time

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Checking ticket price...")
        page.goto(EVENT_URL, timeout=60000)
        page.wait_for_timeout(5000)

        text = page.inner_text("body")
        price = extract_price(text)

        current_time = time.time()

        if price:
            print("Current price:", price)

            # First run
            if last_price is None:
                last_price = price
                send_telegram(f"🎟 Current ticket price: ₹{price}")

            # Price drop alert
            elif price < 5000 and last_price >= 5000:
                send_telegram(f"🚨 Price dropped to ₹{price}!\n{EVENT_URL}")

            # 15-minute status update
            if current_time - last_status_time > 900:
                send_telegram(f"📊 Current ticket price: ₹{price}")
                last_status_time = current_time

            last_price = price

        else:
            print("Price not detected.")

        browser.close()


while True:
    check_tickets()
    time.sleep(120)  # checks every 2 minutes
