from flask import Flask, jsonify, render_template
from datetime import datetime, timezone, timedelta
import csv
import os

app = Flask(__name__)

def load_tide_data():
    """Load and parse the CSV file"""
    csv_path = os.path.join(os.path.dirname(__file__), 'holy_island_2026_2029.csv')
    events = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append({
                'timestamp': row['utc_timestamp'],
                'status': row['status']
            })
    
    return events

def get_current_status():
    """Calculate current causeway status and upcoming events"""
    events = load_tide_data()
    now = datetime.now(timezone.utc)
    
    # Find current status and next event
    current_status = None
    next_event = None
    next_next_event = None
    
    for i, event in enumerate(events):
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        
        if event_time > now:
            if next_event is None:
                next_event = {
                    'timestamp': event['timestamp'],
                    'status': event['status'],
                    'datetime': event_time
                }
                # Current status is opposite of next event
                current_status = 'CLOSED' if event['status'] == 'OPEN' else 'OPEN'
            elif next_next_event is None:
                next_next_event = {
                    'timestamp': event['timestamp'],
                    'status': event['status'],
                    'datetime': event_time
                }
                break
    
    # Get today's and tomorrow's events for the bar charts
    today_events = []
    tomorrow_events = []
    
    now_date = now.date()
    tomorrow_date = (now + timedelta(days=1)).date()
    
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        event_date = event_time.date()
        
        if event_date == now_date:
            today_events.append({
                'timestamp': event['timestamp'],
                'status': event['status']
            })
        elif event_date == tomorrow_date:
            tomorrow_events.append({
                'timestamp': event['timestamp'],
                'status': event['status']
            })
    
    return {
        'current_status': current_status,
        'next_event': next_event,
        'next_next_event': next_next_event,
        'today_events': today_events,
        'tomorrow_events': tomorrow_events,
        'current_time': now.isoformat()
    }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/privacy')
def privacy():
    """Serve the privacy policy page"""
    return render_template('privacy.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify(get_current_status())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
