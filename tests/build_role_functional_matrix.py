#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROLES_DIR = ROOT / "roles"
GLOBAL_TRIGGER_PATHS = (
    ".github/workflows/",
    "tests/",
    "tools/",
    "requirements",
    "galaxy.yml",
    ".ansible-lint",
)
PLATFORM_IMAGE_MAP = {
    "Ubuntu": [{"os_name": "ubuntu-" + v, "image": "ubuntu:" + v} for v in ("22.04", "24.04", "26.04")],
    "Debian": [{"os_name": "debian-13", "image": "debian:13"}],
    "EL": [{"os_name": "rocky-9", "image": "rockylinux:9"}],
}


def iter_functional_roles(role_filter: str | None = None) -> list[Path]:
    role_dirs = sorted(path for path in ROLES_DIR.iterdir() if path.is_dir())
    if role_filter:
        role_dirs = [path for path in role_dirs if path.name == role_filter]
    return [path for path in role_dirs if (path / "tests" / "functional.yml").exists()]


def load_role_platforms(role_dir: Path) -> list[str]:
    meta = yaml.safe_load((role_dir / "meta" / "main.yml").read_text(encoding="utf-8")) or {}
    platforms = meta.get("galaxy_info", {}).get("platforms", [])
    return [item["name"] for item in platforms if item.get("name") in PLATFORM_IMAGE_MAP]


def has_global_trigger_change(changed_files: list[str]) -> bool:
    return any(path.startswith(prefix) or path == prefix for path in changed_files for prefix in GLOBAL_TRIGGER_PATHS)


def resolve_changed_roles(changed_files: list[str], role_filter: str | None = None) -> list[Path]:
    functional_roles = iter_functional_roles(role_filter)
    if role_filter:
        return functional_roles
    if not changed_files:
        return []
    if has_global_trigger_change(changed_files):
        return functional_roles

    changed_role_names = {
        parts[1]
        for path in changed_files
        if (parts := path.split("/", 2)) and len(parts) >= 2 and parts[0] == "roles"
    }
    return [role_dir for role_dir in functional_roles if role_dir.name in changed_role_names]


def build_matrix(role_filter: str | None = None, changed_files: list[str] | None = None) -> dict[str, list[dict[str, str]]]:
    include: list[dict[str, str]] = []

    for role_dir in resolve_changed_roles(changed_files or [], role_filter):
        for platform_name in load_role_platforms(role_dir):
            for platform in PLATFORM_IMAGE_MAP[platform_name]:
                include.append(
                {
                    "role_name": role_dir.name,
                    "playbook": f"roles/{role_dir.name}/tests/functional.yml",
                    "os_name": platform["os_name"],
                    "image": platform["image"],
                }
            )

    return {"include": include}


def main() -> int:
    role_filter = os.environ.get("ROLE_FILTER") or None
    changed_files_env = os.environ.get("CHANGED_FILES", "")
    changed_files = [line for line in changed_files_env.splitlines() if line]
    print(json.dumps(build_matrix(role_filter, changed_files)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
