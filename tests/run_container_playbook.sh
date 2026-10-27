#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:?container image required}"
PLAYBOOK="${2:?playbook required}"
CONTAINER_NAME="degit-test-${GITHUB_RUN_ID:-local}-${RANDOM}"
cleanup() { docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run -d --name "$CONTAINER_NAME" "$IMAGE" sh -c 'while :; do sleep 5; done' >/dev/null
if docker exec "$CONTAINER_NAME" test -f /etc/debian_version; then
  docker exec "$CONTAINER_NAME" sh -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-apt sudo ca-certificates curl iproute2'
else
  docker exec "$CONTAINER_NAME" sh -c 'dnf install -y python3 sudo ca-certificates iproute findutils which tar gzip shadow-utils'
fi
# The controller stays on the runner: Ubuntu 22.04 and EL9 target Python is
# supported by ansible-core, but is too old to run a modern controller.
for run in 1 2; do
  ansible-playbook "$PLAYBOOK" -i "$CONTAINER_NAME," \
    -e ansible_connection=community.docker.docker \
    -e ansible_python_interpreter=/usr/bin/python3 \
    | tee "/tmp/${CONTAINER_NAME}-${run}.log"
done
python3 - "/tmp/${CONTAINER_NAME}-2.log" <<'PY'
from pathlib import Path
import re, sys
text = Path(sys.argv[1]).read_text()
recaps = re.findall(r'^\S+\s+:\s+ok=(\d+)\s+changed=(\d+).*?unreachable=(\d+)\s+failed=(\d+)', text, re.M)
if not recaps or any(int(ok) == 0 or any(int(x) for x in (changed, unreachable, failed)) for ok, changed, unreachable, failed in recaps):
    raise SystemExit('Second run must execute tasks and report changed=0 unreachable=0 failed=0')
PY
