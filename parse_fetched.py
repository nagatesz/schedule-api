from bs4 import BeautifulSoup
import re
import json

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\fetched_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check for Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    print("Found Next.js JSON data!")
    with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\next_data.json", "w") as f:
        f.write(next_data.string)
else:
    # Maybe RSC payload
    print("No __NEXT_DATA__ found. Checking for RSC scripts...")
    scripts = soup.find_all('script')
    for s in scripts:
        if s.string and ('Adv Govt' in s.string or 'Flex Start' in s.string):
            print("Found target string in a script!")
            print(s.string[:500])

# Just to see some text content
print("Text snippet:")
print(soup.body.text[:1000])
