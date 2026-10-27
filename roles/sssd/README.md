# sssd

Configure SSSD for directory integration.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Requires an explicit directory domain. Domain joins additionally require operator credentials. Without a configured domain the role stops before modifying accounts, PAM, sudo or SSH.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
sssd_domain_name: ''
sssd_join_domain: false
sssd_restrict_access: true
sssd_manage_mkhomedir: true
sssd_manage_service: true
sssd_service_enabled: true
sssd_service_state: started
sssd_ad_group_allowed_ssh_and_sudo: Linux-Admins
sssd_ad_group_allowed_ssh_and_sudo_extra: []
sssd_ad_group_allowd_ssh_and_sudo: '{{ sssd_ad_group_allowed_ssh_and_sudo }}'
sssd_ad_group_allowd_ssh_and_sudo_extra: '{{ sssd_ad_group_allowed_ssh_and_sudo_extra }}'
sssd_ou_to_join_servers: ''
sssd_bind_user: ''
sssd_bind_password: ''
sssd_ad_group_allowed_ssh: []
```

## Example Playbook

```yaml
- name: Join directory members
  hosts: directory_members
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.sssd
      vars:
        sssd_domain_name: example.net
        sssd_join_domain: true
        sssd_bind_user: "{{ vault_directory_join_user }}"
        sssd_bind_password: "{{ vault_directory_join_password }}"
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
