#!/bin/bash
# Example script to send metrics using curl

AGENT_URL="http://localhost:8000"

echo "Sending button click metrics..."

for i in {1..10}; do
  curl -X POST "$AGENT_URL/metrics" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"button_clicks\",
      \"value\": 1,
      \"tags\": {\"button\": \"submit\", \"page\": \"home\"},
      \"source\": \"web-app\"
    }"
  echo ""
  sleep 0.5
done

echo "Done! Check the dashboard at http://localhost:3000"

