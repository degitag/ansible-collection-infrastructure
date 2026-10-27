#!/usr/bin/env bash
set -euo pipefail
bash tests/run_container_playbook.sh "${SMOKE_CONTAINER_IMAGE:?SMOKE_CONTAINER_IMAGE is required}" tests/integration/smoke.yml
