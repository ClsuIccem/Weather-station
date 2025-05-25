# Weather Monitoring System

A Python-based weather monitoring system that displays current weather conditions and forecasts.

## Features

- Real-time display of:
  - Air Temperature
  - Relative Humidity
  - Barometric Pressure
- Today's hourly forecast
- 7-day weather forecast
- Modern, responsive design

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
  - `css/` - Stylesheets
  - `js/` - JavaScript files
  - `images/` - Weather icons and images

## Dependencies

- Flask - Web framework
- Requests - HTTP library for API calls
- Python-dotenv - Environment variable management
