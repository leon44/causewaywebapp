# Holy Island Causeway - Tide Times Web App

A minimal Flask web application that displays real-time Holy Island causeway crossing status and tide times.

## Features

- Live causeway status (OPEN/CLOSED) with countdown timer
- iOS app-style design with large status circle
- Today and tomorrow tide visualizations
- SEO optimized for Holy Island searches
- Mobile-first responsive design
- Promotes the full iOS app

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

3. Visit `http://localhost:5000`

## Deployment to DigitalOcean

### Option 1: App Platform (Recommended)

1. Push code to GitHub repository
2. Create new App in DigitalOcean App Platform
3. Connect your repository
4. Configure:
   - **Run Command**: `gunicorn --bind 0.0.0.0:8080 wsgi:app`
   - **HTTP Port**: 8080
   - **Environment**: Python 3.11+
5. Deploy

### Option 2: Droplet with Nginx

1. Create Ubuntu droplet
2. SSH into droplet and install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. Clone repository and setup:
```bash
cd /var/www
git clone <your-repo>
cd <repo-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Create systemd service `/etc/systemd/system/causeway.service`:
```ini
[Unit]
Description=Holy Island Causeway Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/<repo-name>
Environment="PATH=/var/www/<repo-name>/venv/bin"
ExecStart=/var/www/<repo-name>/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

5. Configure Nginx as reverse proxy
6. Enable and start service:
```bash
sudo systemctl enable causeway
sudo systemctl start causeway
```

## Data Source

Tide data is loaded from `holy_island_2026_2029.csv` in the parent directory. The CSV contains UTC timestamps and status (OPEN/CLOSED) events.

## License

All rights reserved.
