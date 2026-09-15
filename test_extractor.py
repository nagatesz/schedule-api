import json
import re

def extract_json(decoded_str):
    # Find the start of "initialDay":
    idx = decoded_str.find('"initialDay":')
    if idx == -1: return None
    
    # We want to extract the value of "initialDay" which is a dict {...}
    # It starts right after "initialDay":
    start_idx = decoded_str.find('{', idx)
    if start_idx == -1: return None
    
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(decoded_str)):
        if decoded_str[i] == '{':
            brace_count += 1
        elif decoded_str[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
                
    if end_idx != -1:
        json_str = decoded_str[start_idx:end_idx]
        return json.loads(json_str)
    return None

with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\rsc_decoded.txt", "r", encoding="utf-8") as f:
    text = f.read()

data = extract_json(text)
print(data['date'])
for b in data['blocks']:
    print(b['name'], b['start'], b['end'])
