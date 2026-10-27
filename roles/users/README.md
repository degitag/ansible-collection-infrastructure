# users

Manage local users, SSH keys, and shell dotfiles.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Root dotfiles and the optional third-party powerline-go binary are disabled by default. Enable them explicitly for the intended operator environment; local accounts and sudo rules remain the primary role responsibility.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
users_defaults: []
users_group_vars: []
users_host_vars: []
users_playbook: []
users_manage_root_dotfiles: false
users_copy_msmtp_config: true
users_powerline_go_enabled: false
users_powerline_go_version: '1.26'
users_powerline_go_install_dir: /usr/local/bin
users_powerline_go_binary_name: powerline-go
users_powerline_go_arch_map:
  x86_64: amd64
  aarch64: arm64
users_powerline_go_checksum: ''
users_groups: []
```

## Example Playbook

```yaml
- name: Apply users
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.users
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
