# API Monitoring Tool (A-grade component)

This project uses **Uptime Kuma** as the monitoring tool.

## Why this fits the brief
- It is an API monitoring tool.
- It provides a dashboard showing uptime, outages, and response times.
- It is easy to run using Docker.
- It gives clear screenshots for the final PDF document.

## How to run it
1. Start the API and MongoDB using Docker Compose:
   ```bash
   docker compose up --build -d mongo api uptime-kuma
   ```
2. Open the monitoring dashboard in your browser:
   - `http://localhost:3001`
3. Create an admin account the first time you open it.
4. Add a new **HTTP(s)** monitor.
5. Set the monitored URL to one of these:
   - `http://api:8000/getAll` when using Docker networking inside Compose
   - `http://localhost:8000/getAll` when monitoring from the host machine
6. Set the heartbeat interval, for example 60 seconds.
7. Save the monitor and let it collect response-time data.

## Screenshots to capture for the report
- Uptime Kuma dashboard
- Added monitor configuration
- Response-time / uptime history graph
- API running at `/docs`
