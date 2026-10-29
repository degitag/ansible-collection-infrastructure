from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.build_role_functional_matrix import build_matrix  # noqa: E402
from tests.build_role_functional_matrix import resolve_changed_roles  # noqa: E402


def test_functional_matrix_includes_dante_and_wpad_across_supported_platforms() -> None:
    matrix = build_matrix(changed_files=["tests/run_role_functional_checks.sh"])
    entries = {(item["role_name"], item["os_name"]) for item in matrix["include"]}

    assert ("dante", "ubuntu-22.04") in entries
    assert ("dante", "debian-13") not in entries
    assert ("dante", "rocky-9") in entries
    assert ("wpad", "ubuntu-22.04") in entries
    assert ("wpad", "debian-13") in entries
    assert ("wpad", "rocky-9") in entries


def test_functional_matrix_can_filter_to_one_role() -> None:
    matrix = build_matrix("wpad")

    assert matrix["include"]
    assert {item["role_name"] for item in matrix["include"]} == {"wpad"}


def test_changed_role_resolution_limits_matrix_to_touched_role_paths() -> None:
    changed_roles = resolve_changed_roles(
        [
            "roles/wpad/tasks/main.yml",
            "roles/wpad/tests/functional.yml",
            "README.md",
        ]
    )

    assert {role.name for role in changed_roles} == {"wpad"}


def test_workflow_outputs_use_real_newlines(tmp_path, monkeypatch):
    import json
    import subprocess
    import yaml
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    command = workflow['jobs']['functional-plan']['steps'][-1]['run']
    script = command.split("python - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
    output = tmp_path / 'github-output'
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))
    monkeypatch.setenv('BASE_SHA', '0' * 40)
    monkeypatch.setattr(subprocess, 'check_output', lambda *args, **kwargs: 'tests/run_container_playbook.sh\n')
    exec(compile(script, '<workflow-matrix>', 'exec'), {})
    lines = output.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0].removeprefix('matrix=')) == build_matrix(changed_files=['tests/run_container_playbook.sh'])
    assert lines[1] == 'has-tests=true'
