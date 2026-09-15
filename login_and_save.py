from playwright.sync_api import sync_playwright
import time
import json
import os

def main():
    profile_dir = r"C:\Users\nagat\Downloads\SCHEDULEwidget\pw_profile"
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome"
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://flex.lkgeorge.org/student/schedule")
        
        print("Please log in. Waiting for you to complete the login process...")
        
        # Wait until the page text contains something from the schedule, or just wait for 2 minutes
        # "Your schedule" or "Back to today"
        try:
            page.wait_for_selector("text=Your schedule", timeout=120000)
            print("Detected login success!")
            
            # Save the cookies!
            cookies = browser.cookies("https://flex.lkgeorge.org")
            with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\cookies.json", "w") as f:
                json.dump(cookies, f)
                
            # Also save the HTML so I can analyze the DOM structure
            html = page.content()
            with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\schedule.html", "w", encoding="utf-8") as f:
                f.write(html)
                
            print("Successfully saved cookies and schedule.html! You can close the browser now.")
            
        except Exception as e:
            print(f"Error or timed out: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
