# keepalived

Install and configure Keepalived VRRP instances and helper scripts.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
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
keepalived_packages:
- keepalived
keepalived_manage_service: true
keepalived_service_enabled: false
keepalived_service_state: stopped
keepalived_config_group_vars: {}
keepalived_config_host_vars: {}
keepalived_config_playbook: {}
keepalived_healthcheck_scripts: []
keepalived_config_defaults:
  global_defs:
    router_id: '{{ inventory_hostname }}'
    script_user: root
    enable_script_security: true
  vrrp_scripts: []
  vrrp_instances: []
keepalived_logrotate_enabled: true
keepalived_logrotate_path: /etc/logrotate.d/keepalived-custom-logs
keepalived_logrotate_config:
  logfile: /var/log/keepalived-snat.log
  frequency: weekly
  rotate: 8
  compress: true
  delaycompress: true
  create_mode: '0640'
  create_owner: root
  create_group: adm
```

## Example Playbook

```yaml
- name: Apply keepalived
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.keepalived
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
