# unattended_updates

Configure unattended upgrades on Debian and Ubuntu.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13

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
unattended_updates_updates_cache_valid_time: 3600
unattended_updates_package_blacklist: []
unattended_updates_autofix_interrupted_dpkg: true
unattended_updates_minimal_steps: true
unattended_updates_install_on_shutdown: false
unattended_updates_mail: "{{ unattended_updates_mail_recipient | default('') }}"
unattended_updates_mail_only_on_error: true
unattended_updates_mail_report: only-on-error
unattended_updates_remove_unused_dependencies: true
unattended_updates_remove_new_unused_dependencies: true
unattended_updates_remove_unused_kernel_packages: true
unattended_updates_automatic_reboot: "{{ unattended_updates_automatic_reboot_enabled | default('true') }}"
unattended_updates_automatic_reboot_time: "{{ '02:%02d' | format(60 | random(seed=inventory_hostname)) }}"
unattended_updates_ignore_apps_require_restart: false
unattended_updates_syslog_enable: true
unattended_updates_syslog_facility: updates
unattended_updates_update_package_list: 1
unattended_updates_download_upgradeable:
unattended_updates_autoclean_interval: 7
unattended_updates_clean_interval: 7
unattended_updates_verbose: 1
unattended_updates_random_sleep: 1800
unattended_updates_update_days:
unattended_updates_dpkg_options: []
unattended_updates_dl_limit: 0
unattended_updates_only_on_ac_power: false
```

## Example Playbook

```yaml
- name: Apply unattended_updates
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.unattended_updates
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
