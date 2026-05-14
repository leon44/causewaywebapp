from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import calendar
import csv
import os

app = Flask(__name__)

def load_tide_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'holy_island_2026_2029.csv')
    events = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append({'timestamp': row['utc_timestamp'], 'status': row['status']})
    return events

def events_by_date(events):
    grouped = defaultdict(list)
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        grouped[event_time.date()].append({'timestamp': event['timestamp'], 'status': event['status']})
    return grouped

def get_current_status():
    events = load_tide_data()
    now = datetime.now(timezone.utc)

    current_status = None
    next_event = None
    next_next_event = None

    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        if event_time > now:
            if next_event is None:
                next_event = {'timestamp': event['timestamp'], 'status': event['status'], 'datetime': event_time}
                current_status = 'CLOSED' if event['status'] == 'OPEN' else 'OPEN'
            elif next_next_event is None:
                next_next_event = {'timestamp': event['timestamp'], 'status': event['status'], 'datetime': event_time}
                break

    grouped = events_by_date(events)
    today_utc = datetime(now.year, now.month, now.day, tzinfo=timezone.utc).date()

    # Last event before today (for today's bleeding period)
    yesterday_date = today_utc - timedelta(days=1)
    yesterday_events = grouped.get(yesterday_date, [])
    yesterday_last_event = yesterday_events[-1] if yesterday_events else None

    upcoming_days = []
    for day_offset in range(15):
        target_date = (now + timedelta(days=day_offset)).date()
        day_events = grouped.get(target_date, [])
        day_name = 'Today' if day_offset == 0 else 'Tomorrow' if day_offset == 1 else (now + timedelta(days=day_offset)).strftime('%A')
        upcoming_days.append({'name': day_name, 'date': target_date.isoformat(), 'events': day_events})

    return {
        'current_status': current_status,
        'next_event': next_event,
        'next_next_event': next_next_event,
        'upcoming_days': upcoming_days,
        'yesterday_last_event': yesterday_last_event,
        'current_time': now.isoformat()
    }

def get_month_data(year, month):
    events = load_tide_data()
    _, days_in_month = calendar.monthrange(year, month)
    grouped = events_by_date(events)
    month_days = []

    for day in range(1, days_in_month + 1):
        target_date = datetime(year, month, day, tzinfo=timezone.utc).date()
        prev_date = target_date - timedelta(days=1)
        next_date = target_date + timedelta(days=1)

        day_events = grouped.get(target_date, [])
        prev_events = grouped.get(prev_date, [])
        next_events = grouped.get(next_date, [])

        month_days.append({
            'date': target_date.isoformat(),
            'events': day_events,
            'prev_last_event': prev_events[-1] if prev_events else None,
            'next_first_event': next_events[0] if next_events else None,
        })

    return {'days': month_days}

@app.route('/')
def index():
    return render_template('new.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/about-causeway')
def about_causeway():
    return render_template('about_causeway.html')

@app.route('/new')
def new():
    return render_template('new.html')


@app.route('/api/month')
def api_month():
    year = int(request.args.get('year', datetime.now(timezone.utc).year))
    month = int(request.args.get('month', datetime.now(timezone.utc).month))
    return jsonify(get_month_data(year, month))

@app.route('/api/status')
def api_status():
    return jsonify(get_current_status())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
