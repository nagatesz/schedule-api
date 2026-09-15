from flask import Flask, jsonify, request
import requests
import json
import re
import os
from datetime import datetime, timedelta
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

def extract_school_days(decoded_str):
    match = re.search(r'"schoolDays":\[(.*?)\]', decoded_str)
    if match:
        try:
            return json.loads("[" + match.group(1) + "]")
        except:
            pass
    return None

def get_schedule_html(cookie_value, date_str=None):
    cookies = {
        '__Secure-authjs.session-token': cookie_value
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    url = 'https://flex.lkgeorge.org/student/schedule'
    if date_str:
        url += f'?date={date_str}'
        
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return None
    return response.text

def parse_schedule_html(html):
    matches = re.findall(r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)', html)
    for m in matches:
        if 'initialDay' in m:
            rsc_str = m
            try:
                decoded_str = json.loads('"' + rsc_str + '"')
                data = extract_json(decoded_str)
                school_days = extract_school_days(decoded_str)
                if data:
                    return data, school_days
            except:
                pass
    return None, None

@app.route('/api/schedule')
def get_schedule():
    cookie = os.environ.get("FLEX_COOKIE", "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiV3VybVpwTnJManc1cEhnYUJSOWJyNDBHdnlsSFlzaHM4RUZrUUQ1aFpsTFFDWGVqLTlhUTFJbU9GWF96Nmt2MDFuRTh3OGUyUjBnaFR0WlM5Z2tQMUEifQ..VCyuLxL9y7FyDnbgiPTFSQ.szPkPc1ktg91mVja_6cO2LmptAYGT9mn1sY4NyMDH3og31VnVFokXM9ZmoMTjDugB9ToapmTKdZaLaIW3A0uqlmy-jgqeS20CE1A7JBGMRxhypMtSeXnKty9zYE8euh-YlJ3m_clq87-Fhx_QTTxemngE4MjhFH8I-uqHw64ZogyJ2jN2G6U7hM_fsSMTIYJjQ8bJqAm_YbwVFU9EVd2hAgm6mB6C8maGnGR69NRuFymlvgyuKi29p0RYveGkHuX_DN2hEsXNncFjx4FXd3rOw3-FBWzBiuEOtt6bs4FfxAHQxmyYQaV_3Mo9MZZXAHhT-4ro6i1HsVYHaMdYVOP0_3Wq9MKQoa7NK8ibU05LldQxmqFHXBWX-6EQgEpowoVF9vFilUxQUpCfF8F1pBiGA.0bcbEEUL0UoTciJWvi3gpD1sTBiailrThQDAQqkL1oI")
    
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    
    # First fetch today (or whatever the default is)
    html = get_schedule_html(cookie)
    if not html:
        return jsonify({"error": "Failed to fetch"})
        
    data, school_days = parse_schedule_html(html)
    
    if data:
        # Check if we should show the NEXT school day
        # e.g., if current time is past 15:15 (3:15 PM) on a school day, 
        # or if today is not a school day (weekend).
        is_after_school = False
        today_str = now.strftime("%Y-%m-%d")
        
        # Determine last block end time for today
        if data.get('blocks') and len(data['blocks']) > 0:
            last_block = data['blocks'][-1]
            try:
                end_h, end_m = map(int, last_block['end'].split(':'))
                end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                if now > end_t:
                    is_after_school = True
            except:
                pass
                
        if today_str not in (school_days or []) or is_after_school:
            # We need to fetch the NEXT school day
            if school_days:
                next_day = None
                for d in school_days:
                    if d > today_str:
                        next_day = d
                        break
                
                if next_day:
                    html_next = get_schedule_html(cookie, date_str=next_day)
                    if html_next:
                        data_next, _ = parse_schedule_html(html_next)
                        if data_next:
                            data = data_next # Swap data out for tomorrow's data!
        
        # Calculate current block for whatever day data is showing
        current_block = None
        data_date = data.get("date")
        
        if data_date == today_str: # Only highlight active block if the data is for TODAY
            for b in data.get('blocks', []):
                try:
                    start_h, start_m = map(int, b['start'].split(':'))
                    end_h, end_m = map(int, b['end'].split(':'))
                    
                    start_t = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    
                    if start_t <= now <= end_t:
                        current_block = b
                        break
                except Exception:
                    continue
                
        custom_data = {
            "date": data.get("date"),
            "letter_day": data.get("letter"),
            "current_block": current_block,
            "all_blocks": data.get("blocks", []),
            "showing_future_day": data_date != today_str,
            "raw_data": data 
        }
        return jsonify(custom_data)
        
    return jsonify({"error": "Could not parse schedule"})

@app.route('/')
def home():
    return jsonify({"status": "running", "endpoint": "/api/schedule"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
