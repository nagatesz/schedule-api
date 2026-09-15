import shutil
import os
import sqlite3

def test_copy():
    appdata = os.getenv('LOCALAPPDATA')
    cookie_db = os.path.join(appdata, r'Google\Chrome\User Data\Default\Network\Cookies')
    temp_db = os.path.join(appdata, r'Temp\temp_cookies.db')
    try:
        shutil.copy2(cookie_db, temp_db)
        print("Successfully copied without admin!")
    except Exception as e:
        print(f"Failed to copy: {e}")

test_copy()
