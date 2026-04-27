#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
fi

ORION_BASE_URL="${ORION_BASE_URL:-http://localhost:1026}"
QUANTUMLEAP_BASE_URL="${QUANTUMLEAP_BASE_URL:-http://localhost:8668}"
IOTA_NORTH_PORT="${IOTA_NORTH_PORT:-4041}"
CRATE_HTTP_PORT="${CRATE_HTTP_PORT:-4200}"
GRAFANA_PORT="${GRAFANA_PORT:-3000}"

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[1;33m'
reset='\033[0m'

status=0

check_container_running() {
  local container="$1"
  if docker ps --format '{{.Names}}' | grep -Fxq "${container}"; then
    echo -e "${green}[OK]${reset} container ${container} running"
  else
    echo -e "${red}[FAIL]${reset} container ${container} not running"
    status=1
  fi
}

check_http() {
  local name="$1"
  local url="$2"

  if curl -fsS "${url}" >/dev/null; then
    echo -e "${green}[OK]${reset} ${name} reachable at ${url}"
  else
    echo -e "${red}[FAIL]${reset} ${name} not reachable at ${url}"
    status=1
  fi
}

echo -e "${yellow}Checking FIWARE base containers...${reset}"
check_container_running "urbanpulse-mongo-db"
check_container_running "urbanpulse-orion-ld"
check_container_running "urbanpulse-mosquitto"
check_container_running "urbanpulse-iot-agent-json"
check_container_running "urbanpulse-crate-db"
check_container_running "urbanpulse-quantumleap"
check_container_running "urbanpulse-grafana"

echo -e "${yellow}Checking service endpoints...${reset}"
check_http "Orion-LD" "${ORION_BASE_URL}/version"
check_http "IoT Agent JSON" "http://localhost:${IOTA_NORTH_PORT}/iot/about"
check_http "QuantumLeap" "${QUANTUMLEAP_BASE_URL}/version"
check_http "CrateDB HTTP" "http://localhost:${CRATE_HTTP_PORT}/"
check_http "Grafana" "http://localhost:${GRAFANA_PORT}/api/health"

if [[ ${status} -eq 0 ]]; then
  echo -e "${green}All FIWARE base services are healthy.${reset}"
else
  echo -e "${red}One or more FIWARE base checks failed.${reset}"
fi

exit ${status}
