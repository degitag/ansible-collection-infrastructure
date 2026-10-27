#!/usr/bin/env bash
set -euo pipefail
ROLE_NAME="${1:?role name required}"
bash tests/run_container_playbook.sh "${2:?container image required}" "roles/${ROLE_NAME}/tests/functional.yml"
