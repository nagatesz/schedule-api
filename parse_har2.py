import json
import sys

har_path = r"C:\Users\nagat\Downloads\flex.lkgeorge.org.har"

with open(har_path, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

for entry in har_data['log']['entries']:
    req = entry['request']
    res = entry['response']
    url = req['url']
    
    text = res['content'].get('text', '')
    if 'Adv Govt' in text or 'Guide Room' in text or 'Flex Start' in text or 'Accounting' in text:
        print("FOUND TEXT!")
        print("URL:", url)
        print("MimeType:", res['content'].get('mimeType'))
        
        for h in req['headers']:
            if h['name'].lower() == 'cookie':
                print("Cookie found (length):", len(h['value']))
                
        print("Response length:", len(text))
        print("---")
