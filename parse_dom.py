from bs4 import BeautifulSoup
import re
import json

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
blocks = []

# Assuming each block is in an 'li' or 'div' with specific class. Let's find all time elements.
times = soup.find_all(string=re.compile(r'\d{1,2}:\d{2}\s[AM|PM]'))
for t in times:
    print(t.parent.text, t.parent.parent.text)

