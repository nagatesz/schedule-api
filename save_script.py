import re
import json

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

script_content = None
import bs4
soup = bs4.BeautifulSoup(html, 'html.parser')
for s in soup.find_all('script'):
    if s.string and 'Guide Room' in s.string:
        script_content = s.string
        break

if script_content:
    with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\script_content.txt", "w", encoding="utf-8") as f:
        f.write(script_content)
    print("Saved script content to script_content.txt")
