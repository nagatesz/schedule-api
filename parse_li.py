from bs4 import BeautifulSoup
import re

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("All list items (li):")
for li in soup.find_all('li'):
    print(li.text.strip())
    print("-")
