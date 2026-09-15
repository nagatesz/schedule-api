import requests
import json
import re

def extract_json(decoded_str):
    idx = decoded_str.find('"initialDay":')
    if idx == -1: return None
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

def get_schedule_data(cookie_value):
    cookies = {
        '__Secure-authjs.session-token': cookie_value
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = 'https://flex.lkgeorge.org/student/schedule'
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return None
        
    html = response.text
    
    matches = re.findall(r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)', html)
    for m in matches:
        if 'initialDay' in m:
            rsc_str = m
            try:
                decoded_str = json.loads('"' + rsc_str + '"')
                data = extract_json(decoded_str)
                if data:
                    return data
            except Exception as e:
                pass
    return None
