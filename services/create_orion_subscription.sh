#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
SUBSCRIPTION_FILE="${ROOT_DIR}/services/subscriptions/orion_to_quantumleap_all_entities.json"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
fi

ORION_BASE_URL="${ORION_BASE_URL:-http://localhost:1026}"
SUBSCRIPTIONS_URL="${ORION_BASE_URL}/ngsi-ld/v1/subscriptions"
DESCRIPTION_MATCH="UrbanPulse Orion-LD to QuantumLeap subscription for all NGSI-LD model entities"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required but not installed."
  exit 1
fi

if [[ ! -f "${SUBSCRIPTION_FILE}" ]]; then
  echo "Subscription payload not found: ${SUBSCRIPTION_FILE}"
  exit 1
fi

echo "Checking Orion-LD availability..."
curl -fsS "${ORION_BASE_URL}/version" >/dev/null

echo "Querying existing subscriptions..."
existing_id="$(curl -fsS \
  -H 'Accept: application/ld+json' \
  "${SUBSCRIPTIONS_URL}" | jq -r --arg desc "${DESCRIPTION_MATCH}" '.[] | select(.description == $desc) | .id' | head -n1)"

if [[ -n "${existing_id}" && "${existing_id}" != "null" ]]; then
  echo "Subscription already exists: ${existing_id}"
  exit 0
fi

echo "Creating Orion-LD subscription for all NGSI-LD model entities..."
location_header="$(curl -isS -X POST \
  "${SUBSCRIPTIONS_URL}" \
  -H 'Content-Type: application/ld+json' \
  -H 'Accept: application/ld+json' \
  --data-binary "@${SUBSCRIPTION_FILE}" | awk 'BEGIN{IGNORECASE=1} /^Location:/ {print $2}' | tr -d '\r')"

if [[ -z "${location_header}" ]]; then
  echo "Subscription creation response did not include Location header."
  exit 1
fi

echo "Subscription created successfully: ${location_header}"
