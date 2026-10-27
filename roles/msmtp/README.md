# msmtp

Configure msmtp relay accounts and aliases.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Requires explicit SMTP accounts and a valid selected default account. Configurations containing credentials are root-readable only and hidden from task output. The role does not send test messages.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
msmtp_auth: "off"
msmtp_tls: "on"
msmtp_tls_starttls: "on"
msmtp_set_from_header: "on"
msmtp_syslog: "on"
msmtp_default_account: default
msmtp_logfile: /var/log/msmtp.log
msmtp_aliases_enabled: true
msmtp_accounts: []
msmtp_aliases:
  root: root
msmtp_tls_trust_file: "{{ _msmtp_platform_tls_trust_file | default('/etc/ssl/certs/ca-certificates.crt') }}"
```

## Example Playbook

```yaml
- name: Configure explicit system mail relay
  hosts: servers
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.msmtp
      vars:
        msmtp_default_account: relay
        msmtp_accounts:
          - name: relay
            host: smtp.example.net
            port: 587
            from: servers@example.net
            auth: "on"
            user: "{{ vault_smtp_user }}"
            password: "{{ vault_smtp_password }}"
```

## Testing

Build and install the current collection checkout before running syntax checks, so the
fully qualified role reference resolves to this implementation.

Run `python tools/generate_role_scaffold.py --check`, `pytest tests/unit` and
`bash tests/run_role_syntax_checks.sh` from the collection root.
CI additionally runs YAML lint, Ansible lint, collection build/install and container smoke tests.
VM functional results are tracked separately; metadata lists intended compatibility,
not proof that every feature has passed on every distribution.

## Dependencies

Install the collection dependencies from `requirements.yml`. Role dependencies:
`[]`.

## Change management

Use check mode where the underlying modules support it. Review the diff before applying
changes. Network, firewall, identity and storage changes need an out-of-band recovery
path. Secrets belong in Ansible Vault or the operator secret store, never in defaults.
