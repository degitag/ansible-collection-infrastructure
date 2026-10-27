#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.venv/bin:$PATH"
export ANSIBLE_HOME="$PWD/.ansible"
export ANSIBLE_COLLECTIONS_PATH="$PWD/.ansible/collections"
python tools/check_repository.py
python tools/generate_role_scaffold.py --check
pytest tests/unit -q
yamllint .
ansible-galaxy collection build --force
artifact="$(python tools/collection_metadata.py artifact)"
python tools/check_collection_artifact.py "$artifact"
ansible-galaxy collection install "$artifact" --force --no-deps
if [[ -f tests/run_preflight_checks.py ]]; then python tests/run_preflight_checks.py; fi
python tests/run_ukhd_extension_render_checks.py
bash tests/run_role_syntax_checks.sh
ansible-lint --offline
bash tests/run_collection_sanity.sh "$artifact"
