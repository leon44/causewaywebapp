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
    
    # Get events for the next 7 days
    upcoming_days = []
    
    for day_offset in range(7):
        target_date = (now + timedelta(days=day_offset)).date()
        day_events = []
        
        for event in events:
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            event_date = event_time.date()
            
            if event_date == target_date:
                day_events.append({
                    'timestamp': event['timestamp'],
                    'status': event['status']
                })
        
        day_name = 'Today' if day_offset == 0 else 'Tomorrow' if day_offset == 1 else (now + timedelta(days=day_offset)).strftime('%A')
        upcoming_days.append({
            'name': day_name,
            'date': target_date.isoformat(),
            'events': day_events
        })
    
    return {
        'current_status': current_status,
        'next_event': next_event,
        'next_next_event': next_next_event,
        'upcoming_days': upcoming_days,
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

@app.route('/support')
def support():
    """Serve the support page"""
    return render_template('support.html')

@app.route('/about')
def about():
    """Serve the about page"""
    return render_template('about.html')

@app.route('/about-causeway')
def about_causeway():
    """Serve the about causeway page"""
    return render_template('about_causeway.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify(get_current_status())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
