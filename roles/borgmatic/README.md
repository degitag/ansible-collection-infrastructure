# borgmatic

Install and configure borgmatic backup jobs and timers.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

 On Rocky/RHEL 9, the role enables the signed Fedora EPEL 9 repository through dnf_repos by default; set borgmatic_manage_epel: false to use an operator-provided package source. RHEL requires valid base/AppStream repositories and any applicable CodeReady Builder entitlement. The uv bootstrap installer is pinned by version and SHA256; update both values together.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
borgmatic_manage_packages: true
borgmatic_package_state: present
borgmatic_install_method: uv
borgmatic_version: 2.1.10
borgmatic_config_dir: /etc/borgmatic
borgmatic_config_file: /etc/borgmatic/config.yaml
borgmatic_environment_file: /etc/borgmatic/borgmatic.env
borgmatic_manage_local_repositories: true
borgmatic_manage_timer: false
borgmatic_timer_enabled: true
borgmatic_timer_state: started
borgmatic_timer_on_calendar: '*-*-* 03:17:00'
borgmatic_timer_randomized_delay_sec: 30m
borgmatic_timer_persistent: true
borgmatic_verbosity: 1
borgmatic_actions: []
borgmatic_environment: {}
borgmatic_config:
  source_directories:
  - /etc
  repositories:
  - path: /var/backups/borgmatic
    label: local
    encryption: none
  keep_daily: 7
  keep_weekly: 4
  keep_monthly: 6
  checks:
  - name: repository
  - name: archives
    frequency: 2 weeks
borgmatic_manage_epel: true
borgmatic_uv_version: 0.13.1
borgmatic_uv_installer_checksum: sha256:7c482d409673a53f4d9bd34ae95c9166be3b8d89ca82f27dd7bca3cab457afff
```

## Example Playbook

```yaml
- name: Apply borgmatic
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.borgmatic
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
