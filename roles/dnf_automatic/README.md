# dnf_automatic

Configure automatic package updates on EL systems.

## Supported platforms

- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Run this role only on hosts assigned to its responsibility. Review the defaults and required inputs before rollout.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
dnf_automatic_manage_service: true
dnf_automatic_service_enabled: true
dnf_automatic_service_state: started
dnf_automatic_apply_updates: "yes"
dnf_automatic_emit_via: email
dnf_automatic_email_from: root@localhost
dnf_automatic_email_to: root@localhost
dnf_automatic_email_host: localhost
dnf_automatic_email_tls: "yes"
dnf_automatic_email_port: 25
dnf_automatic_email_auth: login
dnf_automatic_email_user:
dnf_automatic_email_password:
dnf_automatic_download_updates: "yes"
dnf_automatic_download_updates_command: /usr/bin/dnf-automatic-install
dnf_automatic_random_sleep: '1800'
dnf_automatic_system_package_cache: "yes"
dnf_automatic_upgrade_type: default
dnf_automatic_reboot: when-needed
```

## Example Playbook

```yaml
- name: Apply dnf_automatic
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.dnf_automatic
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
