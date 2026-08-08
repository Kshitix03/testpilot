from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False so you can see the browser
        page = browser.new_page()

        page.goto("https://www.saucedemo.com")

        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")

        # After login, the inventory page has a div with class "inventory_list"
        # We wait up to 5 seconds for it to appear
        inventory = page.query_selector(".inventory_list")

        if inventory:
            print("PASS: logged in and inventory page loaded")
        else:
            print("FAIL: inventory page did not appear after login")

        browser.close()

run()
