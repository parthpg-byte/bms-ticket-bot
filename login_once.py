from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="bms_profile",
        headless=False
    )

    page = browser.new_page()
    page.goto("https://in.bookmyshow.com")

    print("Log in manually, then close the browser.")
    page.wait_for_timeout(120000)  # 2 minutes to log in

    browser.close()
