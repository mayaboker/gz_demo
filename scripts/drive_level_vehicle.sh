#!/usr/bin/env bash
set -euo pipefail

SPEED="${1:-2.0}"
DURATION="${2:-12}"
TOPIC="/model/level_vehicle/cmd_vel"

end_time=$((SECONDS + DURATION))

while (( SECONDS < end_time )); do
  gz topic \
    -t "${TOPIC}" \
    -m gz.msgs.Twist \
    -p "linear: {x: ${SPEED}}"
  sleep 0.2
done

gz topic \
  -t "${TOPIC}" \
  -m gz.msgs.Twist \
  -p "linear: {x: 0.0}, angular: {z: 0.0}"
