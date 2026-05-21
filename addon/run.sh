#!/usr/bin/with-contenv bashio

echo "Starting Finance Assistant..."

# Home Assistant add-on options are usually exposed via bashio or reading options.json
# Here we just run the app. In a real addon, we'd parse /data/options.json for config.

export DATABASE_URL=$(bashio::config 'database_url')

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
