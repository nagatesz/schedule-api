import json
import sys

har_path = r"C:\Users\nagat\Downloads\flex.lkgeorge.org.har"

with open(har_path, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

for entry in har_data['log']['entries']:
    url = entry['request']['url']
    mime = entry['response']['content'].get('mimeType', '')
    print(f"{url} ({mime})")
