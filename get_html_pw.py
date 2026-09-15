from playwright.sync_api import sync_playwright
import time
import os

def main():
    profile_dir = r"C:\Users\nagat\Downloads\SCHEDULEwidget\pw_profile"
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome" # use their actual chrome if possible, or just default chromium
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://flex.lkgeorge.org/student/schedule")
        
        print("Waiting for you to log in and the schedule to load...")
        # Wait up to 60 seconds for a common element in the schedule to appear, e.g. "Your schedule" or "Block"
        try:
            # We don't know the exact selector, so we just wait for the user to login and wait a bit
            page.wait_for_timeout(30000) # wait 30s
            html = page.content()
            with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\schedule.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Successfully saved schedule.html!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
