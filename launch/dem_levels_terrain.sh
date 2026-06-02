#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODEL_PATH="${PROJECT_ROOT}/models"
WORLD_PATH="${PROJECT_ROOT}/worlds/dem_levels_terrain.sdf"

if [[ -n "${GZ_SIM_RESOURCE_PATH:-}" ]]; then
  export GZ_SIM_RESOURCE_PATH="${MODEL_PATH}:${GZ_SIM_RESOURCE_PATH}"
else
  export GZ_SIM_RESOURCE_PATH="${MODEL_PATH}"
fi

exec gz sim -v4 --levels "${WORLD_PATH}"
