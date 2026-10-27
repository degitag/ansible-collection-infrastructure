from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parents[2]


def render_apt_sources(context: dict) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(ROOT / "roles" / "apt_repos" / "templates")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template("repo.sources.j2")
    return template.render(**{**context, "ansible_facts": {key.removeprefix("ansible_"): value for key, value in context.items() if key.startswith("ansible_")}})


def test_apt_sources_renders_signed_by_from_managed_key() -> None:
    rendered = render_apt_sources(
        {
            "apt_repos_manage_keys": True,
            "apt_repos_keyring_directory": "/etc/apt/keyrings",
            "item": {
                "name": "example",
                "uri": "https://packages.example.com/debian",
                "suite": "stable",
                "components": ["main"],
                "key_url": "https://packages.example.com/key.asc",
            },
        }
    )

    assert "Types: deb" in rendered
    assert "URIs: https://packages.example.com/debian" in rendered
    assert "Suites: stable" in rendered
    assert "Components: main" in rendered
    assert "Signed-By: /etc/apt/keyrings/example.asc" in rendered


def test_apt_sources_prefers_explicit_signed_by() -> None:
    rendered = render_apt_sources(
        {
            "apt_repos_manage_keys": True,
            "apt_repos_keyring_directory": "/etc/apt/keyrings",
            "item": {
                "name": "custom",
                "uris": ["https://repo1.example.com", "https://repo2.example.com"],
                "suites": ["bookworm"],
                "components": ["main", "contrib"],
                "signed_by": "/usr/share/keyrings/custom.gpg",
                "architectures": ["amd64"],
            },
        }
    )

    assert "URIs: https://repo1.example.com https://repo2.example.com" in rendered
    assert "Components: main contrib" in rendered
    assert "Architectures: amd64" in rendered
    assert "Signed-By: /usr/share/keyrings/custom.gpg" in rendered
