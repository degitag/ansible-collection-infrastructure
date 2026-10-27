# packages

Install and remove packages from aggregated package lists.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Installs a conservative platform baseline plus group, host and playbook additions. Package removal and EPEL installation are opt-in. Override packages_defaults_install to replace the baseline; no role variables override inventory inputs.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
packages_epel_release: false
packages_manage_cache: true
packages_group_vars_install: []
packages_group_vars_install_epel: []
packages_group_vars_remove: []
packages_host_vars_install: []
packages_host_vars_install_epel: []
packages_host_vars_remove: []
packages_playbook_install: []
packages_playbook_install_epel: []
packages_playbook_remove: []
packages_defaults_install: '{{ _packages_platform_install | default([]) }}'
packages_defaults_install_epel: []
packages_defaults_remove: []
```

## Example Playbook

```yaml
- name: Apply packages
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.packages
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
