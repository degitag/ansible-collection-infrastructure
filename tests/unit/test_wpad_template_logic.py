from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "roles" / "wpad" / "templates"


def render_proxy_pac(context: dict) -> str:
    environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("proxy.pac.j2")
    return template.render(**{**context, "ansible_facts": {key.removeprefix("ansible_"): value for key, value in context.items() if key.startswith("ansible_")}})


def test_proxy_pac_builds_default_return_chain_from_targets() -> None:
    rendered = render_proxy_pac(
        {
            "ansible_managed": "managed",
            "wpad_return_string": "",
            "wpad_proxy_targets": [{"type": "PROXY", "host": "proxy.example.com", "port": 3128}],
            "wpad_direct_fallback": True,
            "wpad_bypass_plain_hostnames": True,
            "wpad_bypass_localhost": True,
            "wpad_bypass_exact_hosts": ["localhost"],
            "wpad_bypass_domain_suffixes": [".local"],
            "wpad_bypass_host_globs": [],
            "wpad_bypass_networks": [],
            "wpad_custom_rules": [],
            "wpad_extra_pac_logic": "",
        }
    )

    assert 'return "PROXY proxy.example.com:3128; DIRECT";' in rendered
    assert 'if (isPlainHostName(host))' in rendered
    assert 'dnsDomainIs(hostLower, ".local")' in rendered


def test_proxy_pac_uses_explicit_return_string_and_custom_rules() -> None:
    rendered = render_proxy_pac(
        {
            "ansible_managed": "managed",
            "wpad_return_string": "PROXY proxy-a.example.com:8080; PROXY proxy-b.example.com:8080; DIRECT",
            "wpad_proxy_targets": [],
            "wpad_direct_fallback": False,
            "wpad_bypass_plain_hostnames": False,
            "wpad_bypass_localhost": False,
            "wpad_bypass_exact_hosts": [],
            "wpad_bypass_domain_suffixes": [],
            "wpad_bypass_host_globs": [],
            "wpad_bypass_networks": [],
            "wpad_custom_rules": [{"condition": 'dnsDomainIs(hostLower, ".example.org")', "return": "DIRECT"}],
            "wpad_extra_pac_logic": "",
        }
    )

    assert 'if (dnsDomainIs(hostLower, ".example.org"))' in rendered
    assert 'return "DIRECT";' in rendered
    assert 'return "PROXY proxy-a.example.com:8080; PROXY proxy-b.example.com:8080; DIRECT";' in rendered
