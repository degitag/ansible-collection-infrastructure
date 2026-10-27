# logrotate

Manage custom logrotate rules for application and service logs.

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
logrotate_manage_package: true
logrotate_package_state: present
logrotate_config_dir: /etc/logrotate.d
logrotate_file_prefix: degit-
logrotate_prune_managed_files: false
logrotate_rule_defaults:
  state: present
  frequency: weekly
  rotate: 8
  missingok: true
  notifempty: true
  compress: true
  delaycompress: false
  copytruncate: false
  sharedscripts: false
  dateext: false
  dateyesterday: false
  create: false
  create_mode: '0640'
  create_owner: root
  create_group: root
  su_user:
  su_group:
  olddir:
  extension:
  dateformat:
  size:
  minsize:
  maxsize:
  minage:
  maxage:
  start:
  mail:
  mailfirst: false
  maillast: false
  firstaction: ''
  prerotate: ''
  postrotate: ''
  lastaction: ''
  extra_directives: []
logrotate_rules: []
```

## Example Playbook

```yaml
- name: Configure custom log rotation policies
  hosts: linux_hosts
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.logrotate
      vars:
        logrotate_rules:
          - name: myapp
            paths:
              - /var/log/myapp/*.log
            frequency: daily
            rotate: 14
            compress: true
            delaycompress: true
            create: true
            create_mode: "0640"
            create_owner: myapp
            create_group: myapp
            sharedscripts: true
            postrotate: |
              systemctl reload myapp.service >/dev/null 2>&1 || true
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
