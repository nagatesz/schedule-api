from flask import Flask, jsonify, request, render_template_string
import requests
import json
import re
import os
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# --- HTML TEMPLATE FOR THE MAINFRAME UI ---
MAINFRAME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schedule API Mainframe</title>
    <style>
        body {
            background-color: #0D0D12;
            color: #00FF41;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            border-bottom: 2px solid #00FF41;
            padding-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .container {
            width: 100%;
            max-width: 800px;
            background: #111118;
            border: 1px solid #00FF41;
            box-shadow: 0 0 10px #00FF41;
            padding: 20px;
            border-radius: 5px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        input[type="date"], input[type="text"] {
            background: #000;
            color: #00FF41;
            border: 1px solid #00FF41;
            padding: 10px;
            font-family: inherit;
            outline: none;
        }
        button {
            background: #00FF41;
            color: #000;
            border: none;
            padding: 10px 15px;
            font-weight: bold;
            font-family: inherit;
            cursor: pointer;
            text-transform: uppercase;
            transition: all 0.2s;
        }
        button:hover {
            background: #00CC33;
            box-shadow: 0 0 8px #00FF41;
        }
        pre {
            background: #000;
            color: #00FF41;
            padding: 15px;
            border: 1px solid #333;
            overflow-x: auto;
            max-height: 500px;
            white-space: pre-wrap;
        }
        .terminal-header {
            margin-top: 0;
            color: #00FF41;
            font-size: 0.9em;
        }
    </style>
</head>
<body>

    <h1>// SYSTEM.MAINFRAME //</h1>
    
    <div class="container">
        <div class="controls">
            <button onclick="fetchAPI('')">Fetch Live (Auto)</button>
            <input type="date" id="datePicker">
            <button onclick="fetchCustomDate()">Query Specific Date</button>
        </div>
        
        <p class="terminal-header">Awaiting command...</p>
        <pre id="output">Initialize connection to view data stream.</pre>
    </div>

    <script>
        function setOutput(text) {
            document.getElementById('output').textContent = text;
        }

        async function fetchAPI(queryParam) {
            const url = '/api/schedule' + queryParam;
            document.querySelector('.terminal-header').textContent = `> EXEC: GET ${url}...`;
            setOutput("Loading data stream...");
            try {
                const response = await fetch(url);
                const data = await response.json();
                setOutput(JSON.stringify(data, null, 2));
            } catch (err) {
                setOutput("ERROR: Connection failed.\\n" + err);
            }
        }

        function fetchCustomDate() {
            const dateVal = document.getElementById('datePicker').value;
            if (!dateVal) {
                alert("Please select a date first.");
                return;
            }
            fetchAPI('?date=' + dateVal);
        }
    </script>
</body>
</html>
"""

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
    cookies = {'__Secure-authjs.session-token': cookie_value}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
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
    
    # Check if user requested a specific date via query params
    requested_date = request.args.get('date')
    
    html = get_schedule_html(cookie, date_str=requested_date)
    if not html:
        return jsonify({"error": "Failed to fetch"})
        
    data, school_days = parse_schedule_html(html)
    
    if data:
        # If they didn't request a specific date, apply the auto-tomorrow logic
        if not requested_date:
            is_after_school = False
            today_str = now.strftime("%Y-%m-%d")
            
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
                                data = data_next 

        current_block = None
        data_date = data.get("date")
        today_str = now.strftime("%Y-%m-%d")
        
        if data_date == today_str: 
            for b in data.get('blocks', []):
                try:
                    start_h, start_m = map(int, b['start'].split(':'))
                    end_h, end_m = map(int, b['end'].split(':'))
                    start_t = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    end_t = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    
                    if start_t <= now <= end_t:
                        current_block = b
                        break
                except:
                    continue
                
        custom_data = {
            "date": data.get("date"),
            "letter_day": data.get("letter"),
            "current_block": current_block,
            "all_blocks": data.get("blocks", []),
            "showing_future_day": data_date != today_str and not requested_date,
            "is_custom_query": requested_date is not None,
            "raw_data": data 
        }
        return jsonify(custom_data)
        
    return jsonify({"error": "Could not parse schedule"})

@app.route('/')
def home():
    return render_template_string(MAINFRAME_HTML)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
