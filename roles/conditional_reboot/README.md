# conditional_reboot

Schedule requirement-based reboots within an explicit maintenance window.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Disabled by default. Uses local host time and a bounded maintenance window; missed timer runs are not replayed. Debian/Ubuntu use reboot-required; EL9 uses needs-restarting -r (dnf-utils). A failed requirement check refuses to reboot. The Python controller supports --dry-run and logs without shell interpolation. A disabled configuration cannot reboot even if its service is manually invoked. conditional_reboot_manage_service: false renders artifacts without reloading or activating timers. Remove the old UKHD /usr/local/bin/reboot-check.sh separately after migration; the unit now uses one consistent script path. Test activation and actual reboot on a disposable VM.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
conditional_reboot_enabled: false
conditional_reboot_manage_service: true
conditional_reboot_time:
  hour: 4
  minute: 0
conditional_reboot_day_filter_enabled: true
conditional_reboot_day_of_week: 3
conditional_reboot_day_of_month_range:
- 1
- 7
conditional_reboot_window_minutes: 15
conditional_reboot_log_path: /var/log/conditional_reboot.log
```

## Example Playbook

```yaml
- name: Configure maintenance reboot policy
  hosts: maintenance_hosts
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.conditional_reboot
      vars:
        conditional_reboot_enabled: true
        conditional_reboot_time:
          hour: 4
          minute: 0
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
