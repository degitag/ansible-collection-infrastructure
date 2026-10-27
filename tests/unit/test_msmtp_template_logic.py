from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "roles" / "msmtp" / "templates"


def render_msmtprc(context: dict) -> str:
    environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)
    environment.filters["comment"] = lambda value: f"# {value}"
    environment.filters["bool"] = bool
    template = environment.get_template("msmtprc.j2")
    return template.render(**{**context, "ansible_facts": {key.removeprefix("ansible_"): value for key, value in context.items() if key.startswith("ansible_")}})


def test_msmtprc_uses_auth_off_without_credentials() -> None:
    rendered = render_msmtprc(
        {
            "ansible_managed": "managed",
            "ansible_hostname": "relay",
            "ansible_domain": "",
            "msmtp_auth": "off",
            "msmtp_tls": "on",
            "msmtp_tls_starttls": "on",
            "msmtp_tls_trust_file": "/etc/ssl/certs/ca-certificates.crt",
            "msmtp_set_from_header": "on",
            "msmtp_syslog": "on",
            "msmtp_logfile": "/var/log/msmtp.log",
            "msmtp_aliases_enabled": False,
            "msmtp_aliases_file": "/etc/aliases",
            "msmtp_default_account": "relay",
            "msmtp_accounts": [
                {
                    "name": "relay",
                    "host": "smtp.example.com",
                    "port": 25,
                    "tls": "off",
                    "tls_starttls": "off",
                }
            ],
        }
    )

    assert "account relay" in rendered
    assert "auth off" in rendered
    assert "user " not in rendered
    assert "password " not in rendered
    assert "tls off" in rendered
    assert "tls_trust_file /etc/ssl/certs/ca-certificates.crt" not in rendered
    assert "account default : relay" in rendered


def test_msmtprc_enables_auth_when_account_credentials_are_present() -> None:
    rendered = render_msmtprc(
        {
            "ansible_managed": "managed",
            "ansible_hostname": "relay",
            "ansible_domain": "example.com",
            "msmtp_auth": "off",
            "msmtp_tls": "on",
            "msmtp_tls_starttls": "on",
            "msmtp_tls_trust_file": "/etc/ssl/certs/ca-certificates.crt",
            "msmtp_set_from_header": "on",
            "msmtp_syslog": "on",
            "msmtp_logfile": "/var/log/msmtp.log",
            "msmtp_aliases_enabled": True,
            "msmtp_aliases_file": "/etc/aliases",
            "msmtp_default_account": "default",
            "msmtp_accounts": [
                {
                    "name": "default",
                    "host": "smtp.example.com",
                    "port": 587,
                    "from": "user@example.com",
                    "user": "user@example.com",
                    "password": "secret",
                }
            ],
        }
    )

    assert "auth on" in rendered
    assert "user user@example.com" in rendered
    assert "password secret" in rendered
    assert "tls_trust_file /etc/ssl/certs/ca-certificates.crt" in rendered
    assert "aliases         /etc/aliases" in rendered
