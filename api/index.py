from flask import Flask, jsonify
import requests
import json
import re
import os
from datetime import datetime
import pytz

app = Flask(__name__)

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    url = 'https://flex.lkgeorge.org/student/schedule'
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch"}
        
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
            except:
                pass
    return {"error": "Could not parse schedule"}

@app.route('/api/schedule')
def get_schedule():
    cookie = os.environ.get("FLEX_COOKIE", "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiV3VybVpwTnJManc1cEhnYUJSOWJyNDBHdnlsSFlzaHM4RUZrUUQ1aFpsTFFDWGVqLTlhUTFJbU9GWF96Nmt2MDFuRTh3OGUyUjBnaFR0WlM5Z2tQMUEifQ..VCyuLxL9y7FyDnbgiPTFSQ.szPkPc1ktg91mVja_6cO2LmptAYGT9mn1sY4NyMDH3og31VnVFokXM9ZmoMTjDugB9ToapmTKdZaLaIW3A0uqlmy-jgqeS20CE1A7JBGMRxhypMtSeXnKty9zYE8euh-YlJ3m_clq87-Fhx_QTTxemngE4MjhFH8I-uqHw64ZogyJ2jN2G6U7hM_fsSMTIYJjQ8bJqAm_YbwVFU9EVd2hAgm6mB6C8maGnGR69NRuFymlvgyuKi29p0RYveGkHuX_DN2hEsXNncFjx4FXd3rOw3-FBWzBiuEOtt6bs4FfxAHQxmyYQaV_3Mo9MZZXAHhT-4ro6i1HsVYHaMdYVOP0_3Wq9MKQoa7NK8ibU05LldQxmqFHXBWX-6EQgEpowoVF9vFilUxQUpCfF8F1pBiGA.0bcbEEUL0UoTciJWvi3gpD1sTBiailrThQDAQqkL1oI")
    data = get_schedule_data(cookie)
    
    if data and "error" not in data:
        # Determine the current block based on Eastern Time
        tz = pytz.timezone('America/New_York')
        now = datetime.now(tz)
        current_block = None
        
        for b in data.get('blocks', []):
            try:
                start_h, start_m = map(int, b['start'].split(':'))
                end_h, end_m = map(int, b['end'].split(':'))
                
                # Check if now is within this block
                start_t = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                
                if start_t <= now <= end_t:
                    current_block = b
                    break
            except Exception:
                continue
                
        # Inject custom fields so the client doesn't have to calculate them
        custom_data = {
            "date": data.get("date"),
            "letter_day": data.get("letter"),
            "current_block": current_block,
            "all_blocks": data.get("blocks", []),
            "raw_data": data # keep original data just in case
        }
        return jsonify(custom_data)
        
    return jsonify(data)

@app.route('/')
def home():
    return jsonify({"status": "running", "endpoint": "/api/schedule"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
