from bs4 import BeautifulSoup
import re

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

element = soup.find(string=re.compile('Guide Room'))
if element:
    parent = element.parent
    while parent and parent.name != 'body':
        print(parent.name, parent.get('class'))
        parent = parent.parent
