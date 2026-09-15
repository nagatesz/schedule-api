from bs4 import BeautifulSoup
import re
import json

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# The schedule blocks are likely in a list or specific divs.
# Let's find all the times and get their parent structures.
schedule_items = []
times = soup.find_all(string=re.compile(r'\b\d{1,2}:\d{2}\s[AM|PM]{2}\b'))

for t in times:
    parent = t.parent
    while parent and parent.name not in ['li', 'a'] and 'ss-block' not in parent.get('class', []):
        if parent.get('class') and any('block' in c.lower() or 'item' in c.lower() or 'row' in c.lower() for c in parent.get('class', [])):
            break
        parent = parent.parent
        
    if parent and parent not in schedule_items:
        schedule_items.append(parent)

for idx, item in enumerate(schedule_items):
    print(f"--- Item {idx} ---")
    print(item.text)
