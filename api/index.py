from flask import Flask, jsonify, request, render_template_string
import requests
import json
import re
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Simple file-based state for Vercel serverless (lasts as long as the instance is warm)
STATE_FILE = '/tmp/api_state.json'

def get_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"override_date": None, "logs": []}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except:
        pass

def add_log(msg):
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz).strftime("%I:%M:%S %p")
    state = get_state()
    state['logs'].insert(0, f"[{now}] {msg}")
    if len(state['logs']) > 30:
        state['logs'] = state['logs'][:30] # Keep last 30 logs
    save_state(state)



def extract_json(decoded_str):
    idx = decoded_str.find('"initialDay":')
    if idx == -1: return None
    start_idx = decoded_str.find('{', idx)
    if start_idx == -1: return None
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(decoded_str)):
        if decoded_str[i] == '{': brace_count += 1
        elif decoded_str[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    if end_idx != -1:
        return json.loads(decoded_str[start_idx:end_idx])
    return None

def extract_school_days(decoded_str):
    match = re.search(r'"schoolDays":\[(.*?)\]', decoded_str)
    if match:
        try: return json.loads("[" + match.group(1) + "]")
        except: pass
    return None

def get_schedule_html(cookie_value, date_str=None):
    cookies = {'__Secure-authjs.session-token': cookie_value}
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://flex.lkgeorge.org/student/schedule'
    if date_str: url += f'?date={date_str}'
    add_log(f"Fetching from school server: {url}")
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        add_log(f"Error fetching from school: HTTP {response.status_code}")
        return None
    return response.text

def parse_schedule_html(html):
    matches = re.findall(r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)', html)
    for m in matches:
        if 'initialDay' in m:
            rsc_str = m
            try:
                decoded_str = json.loads('"' + rsc_str + '"')
                return extract_json(decoded_str), extract_school_days(decoded_str)
            except: pass
    return None, None

@app.route('/api/state', methods=['GET', 'POST'])
def manage_state():
    if request.method == 'POST':
        data = request.json
        state = get_state()
        if 'override_date' in data:
            state['override_date'] = data['override_date']
            if data['override_date']:
                add_log(f"USER OVERRIDE SET: Forcing API to return {data['override_date']}")
            else:
                add_log("USER OVERRIDE CLEARED: Returning to Auto Mode")
        save_state(state)
        return jsonify({"success": True})
    return jsonify(get_state())

@app.route('/api/schedule')
def get_schedule():
    cookie = os.environ.get("FLEX_COOKIE", "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiV3VybVpwTnJManc1cEhnYUJSOWJyNDBHdnlsSFlzaHM4RUZrUUQ1aFpsTFFDWGVqLTlhUTFJbU9GWF96Nmt2MDFuRTh3OGUyUjBnaFR0WlM5Z2tQMUEifQ..VCyuLxL9y7FyDnbgiPTFSQ.szPkPc1ktg91mVja_6cO2LmptAYGT9mn1sY4NyMDH3og31VnVFokXM9ZmoMTjDugB9ToapmTKdZaLaIW3A0uqlmy-jgqeS20CE1A7JBGMRxhypMtSeXnKty9zYE8euh-YlJ3m_clq87-Fhx_QTTxemngE4MjhFH8I-uqHw64ZogyJ2jN2G6U7hM_fsSMTIYJjQ8bJqAm_YbwVFU9EVd2hAgm6mB6C8maGnGR69NRuFymlvgyuKi29p0RYveGkHuX_DN2hEsXNncFjx4FXd3rOw3-FBWzBiuEOtt6bs4FfxAHQxmyYQaV_3Mo9MZZXAHhT-4ro6i1HsVYHaMdYVOP0_3Wq9MKQoa7NK8ibU05LldQxmqFHXBWX-6EQgEpowoVF9vFilUxQUpCfF8F1pBiGA.0bcbEEUL0UoTciJWvi3gpD1sTBiailrThQDAQqkL1oI")
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    
    state = get_state()
    requested_date = request.args.get('date')
    
    # If a widget calls without a date, but we have an override, apply the override!
    if not requested_date and state.get('override_date'):
        requested_date = state['override_date']
        add_log(f"Widget requested schedule. Applying active override: {requested_date}")
    elif not requested_date:
        add_log("Widget requested schedule (Auto Mode). Evaluating current time...")
    else:
        add_log(f"Manual query requested for date: {requested_date}")
    
    html = get_schedule_html(cookie, date_str=requested_date)
    if not html: return jsonify({"error": "Failed to fetch"})
        
    data, school_days = parse_schedule_html(html)
    
    if data:
        if not requested_date:
            is_after_school = False
            today_str = now.strftime("%Y-%m-%d")
            
            if data.get('blocks') and len(data['blocks']) > 0:
                try:
                    end_h, end_m = map(int, data['blocks'][-1]['end'].split(':'))
                    end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    if now > end_t: is_after_school = True
                except: pass
                    
            if today_str not in (school_days or []) or is_after_school:
                add_log("API Thinking: School is out for today. Searching for the next available school day...")
                if school_days:
                    next_day = next((d for d in school_days if d > today_str), None)
                    if next_day:
                        add_log(f"API Thinking: Found next school day -> {next_day}")
                        html_next = get_schedule_html(cookie, date_str=next_day)
                        if html_next:
                            data_next, _ = parse_schedule_html(html_next)
                            if data_next: data = data_next 

        current_block = None
        data_date = data.get("date")
        today_str = now.strftime("%Y-%m-%d")
        
        # Only highlight the active block if the data we are looking at is actually TODAY
        if data_date == today_str and not (state.get('override_date') and requested_date == state['override_date']): 
            for b in data.get('blocks', []):
                try:
                    start_h, start_m = map(int, b['start'].split(':'))
                    end_h, end_m = map(int, b['end'].split(':'))
                    start_t = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    
                    if start_t <= now <= end_t:
                        current_block = b
                        add_log(f"API Thinking: Current active block identified as {b['name']}")
                        break
                except: continue
                
        custom_data = {
            "date": data.get("date"),
            "letter_day": data.get("letter"),
            "current_block": current_block,
            "all_blocks": data.get("blocks", []),
            "showing_future_day": data_date != today_str and not requested_date,
            "is_custom_query": requested_date is not None,
            "raw_data": data 
        }
        add_log("Successfully compiled JSON response. Sending to client.")
        return jsonify(custom_data)
        
    add_log("Error: Could not parse schedule from school HTML.")
    return jsonify({"error": "Could not parse schedule"})

@app.route('/')
def home():
    html_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    return "Dashboard not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
