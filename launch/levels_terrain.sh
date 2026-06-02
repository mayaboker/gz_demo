#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODEL_PATH="${PROJECT_ROOT}/models"
WORLD_PATH="${PROJECT_ROOT}/worlds/levels_terrain.sdf"
AUTO_DRIVE="${AUTO_DRIVE:-0}"
AUTO_DRIVE_DELAY="${AUTO_DRIVE_DELAY:-3}"
AUTO_DRIVE_SPEED="${AUTO_DRIVE_SPEED:-1.2}"
AUTO_DRIVE_DURATION="${AUTO_DRIVE_DURATION:-16}"

if [[ -n "${GZ_SIM_RESOURCE_PATH:-}" ]]; then
  export GZ_SIM_RESOURCE_PATH="${MODEL_PATH}:${GZ_SIM_RESOURCE_PATH}"
else
  export GZ_SIM_RESOURCE_PATH="${MODEL_PATH}"
fi



set +e
gz sim --levels "${WORLD_PATH}"
sim_status="$?"
set -e



exit "${sim_status}"
