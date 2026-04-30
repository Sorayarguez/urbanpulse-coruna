#!/usr/bin/env bash
# Simple helper to export dashboards from Grafana via API
GRAFANA_URL=${GRAFANA_URL:-http://localhost:3000}
API_KEY=${GRAFANA_API_KEY:-}
OUT_DIR="grafana/dashboards"
mkdir -p "$OUT_DIR"
if [ -z "$API_KEY" ]; then
  echo "Set GRAFANA_API_KEY to export dashboards"
  exit 1
fi
for uid in vison-general correlacion-trafico-no2 alertas-anomalias prediccion-ml; do
  echo "Exporting $uid"
  curl -s -H "Authorization: Bearer $API_KEY" "$GRAFANA_URL/api/dashboards/uid/$uid" | jq . > "$OUT_DIR/$uid.json"
done
