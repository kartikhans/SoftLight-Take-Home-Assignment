from playwright.sync_api import sync_playwright
import time

AUTH_FILE = "auth_state_linear.json"
START_URL = "https://linear.app/login"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context()
    page = context.new_page()
    page.goto(START_URL)

    print("Once you are logged in and on the main dashboard, press Enter here...")

    # This pauses the script, giving you time to log in manually
    # in the Playwright-controlled browser.
    input()

    # After you press Enter, the script saves the session
    context.storage_state(path=AUTH_FILE)
    print(f"Authentication state saved to {AUTH_FILE}")

    browser.close()