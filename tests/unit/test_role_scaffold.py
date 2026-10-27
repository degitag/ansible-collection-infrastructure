from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.generate_role_scaffold import build_role_files, iter_role_dirs, load_config  # noqa: E402


def test_generated_role_files_are_current() -> None:
    config = load_config()

    for role_dir in iter_role_dirs():
        generated = build_role_files(config, role_dir)
        for path, expected in generated.items():
            assert path.exists(), f"Missing generated file: {path}"
            assert path.read_text(encoding="utf-8") == f"{expected.rstrip()}\n"


def test_new_role_scaffold_includes_the_complete_entry_and_platform_layer(tmp_path) -> None:
    role = tmp_path / 'sample_role'
    role.mkdir()
    generated = build_role_files(load_config(), role)
    for relative in ('defaults/main.yml', 'tasks/main.yml', 'tasks/configuration.yml', 'tasks/preflight.yml', 'vars/platform/Debian.yml', 'vars/platform/Ubuntu-26.04.yml', 'vars/platform/Rocky-9.yml'):
        assert role / relative in generated


def test_syntax_playbooks_reference_the_actual_collection_role() -> None:
    import yaml
    config = load_config()
    for role in iter_role_dirs():
        play = yaml.safe_load(build_role_files(config, role)[role / 'tests/test.yml'])[0]
        assert play['roles'][0]['role'] == f"{config['collection_namespace']}.{config['collection_name']}.{role.name}"
