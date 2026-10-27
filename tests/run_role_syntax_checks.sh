#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
shopt -s nullglob
for playbook in roles/*/tests/test.yml roles/*/tests/functional.yml playbooks/*.yml tests/integration/*.yml; do
  # Example inventories are data, not playbooks.
  [[ "$playbook" == *.example.yml ]] && continue
  ansible-playbook --syntax-check "$playbook" -i localhost,
done
