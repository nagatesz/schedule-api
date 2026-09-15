import json
import sys

har_path = r"C:\Users\nagat\Downloads\flex.lkgeorge.org.har"

with open(har_path, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

for entry in har_data['log']['entries']:
    req = entry['request']
    res = entry['response']
    url = req['url']
    
    # We are looking for schedule data, which probably has JSON response
    if 'mimeType' in res['content'] and 'json' in res['content']['mimeType']:
        text = res['content'].get('text', '')
        # Check if the response contains one of the classes from the screenshot
        if 'Adv Govt' in text or 'Guide Room' in text or 'Flex Start' in text or 'Accounting' in text:
            print("FOUND SCHEDULE API!")
            print("URL:", url)
            print("Method:", req['method'])
            print("Headers (keys):", [h['name'] for h in req['headers']])
            
            # Extract Cookie
            for h in req['headers']:
                if h['name'].lower() == 'cookie':
                    print("Cookie found (length):", len(h['value']))
            
            # Print a snippet of the response
            print("Response length:", len(text))
            print("Response snippet:", text[:1000])
            print("-" * 50)
