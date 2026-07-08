# AirPollutionAI

A Flask-based web application that provides live air quality information, route planning, and interactive dashboards. Features include theme toggling, voice commands (English and Tamil), and now user profiles with customizable preferences.

## Features

- Live AQI updates via Socket.IO
- Dark / light mode toggle
- Voice command support for navigation and actions (in English/Tamil)
- **Administrator login** protecting the dashboard (credentials configurable via `ADMIN_USER`/`ADMIN_PASS` environment variables)
- Responsive, animated frontend with offline fallback

## Getting Started

Install dependencies:

```sh
pip install -r requirements.txt
```

Run the application:

```sh
python run.py
```

Open `http://localhost:5000` in your browser.

## API Endpoints

The project primarily exposes AQI and routing APIs. Authentication is currently limited to the administrator account; there are no public profile endpoints.

- `GET /api/current-aqi` – retrieve AQI for coordinates
- `GET /api/safe-route` – calculate a safe route between two points

(Previous profile endpoints have been removed in favour of a simple login system.)


## Testing

A couple of basic tests verify that the profile service works. Pytest is used, so install it manually (it is not required at runtime):

```sh
pip install pytest
python -m pytest -q
```

## Notes

The project is intended as a demo. An administrator panel is protected by a hardcoded (but configurable) username/password pair stored in environment variables or `.env` file. For production use, integrate a proper user management system.

If you want to change the credentials, set `ADMIN_USER` and `ADMIN_PASS` before starting the app. Defaults are `admin`/`password` for development.
