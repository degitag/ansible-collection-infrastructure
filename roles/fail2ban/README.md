# fail2ban

Install and configure Fail2ban jails and actions.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

 On Rocky/RHEL 9, the role enables the signed Fedora EPEL 9 repository through dnf_repos by default; set fail2ban_manage_epel: false to use an operator-provided package source. RHEL requires valid base/AppStream repositories and any applicable CodeReady Builder entitlement.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
fail2ban_manage_service: true
fail2ban_service_enabled: true
fail2ban_service_state: started
fail2ban_mail_recipient: root@localhost
fail2ban_loglevel: INFO
fail2ban_logtarget: /var/log/fail2ban.log
fail2ban_syslog_target: /var/log/fail2ban.log
fail2ban_syslog_facility: 1
fail2ban_socket: /var/run/fail2ban/fail2ban.sock
fail2ban_pidfile: /var/run/fail2ban/fail2ban.pid
fail2ban_sendername: '{{ ansible_facts.fqdn | default(inventory_hostname) }}'
fail2ban_ignoreips:
- 127.0.0.0/8
- ::1
fail2ban_bantime: 600
fail2ban_maxretry: 3
fail2ban_findtime: 600
fail2ban_backend: systemd
fail2ban_destemail: '{{ fail2ban_mail_recipient }}'
fail2ban_banaction: nftables-multiport
fail2ban_allowipv6: auto
fail2ban_sender:
fail2ban_mta:
fail2ban_protocol:
fail2ban_chain:
fail2ban_jails:
- name: sshd
  enabled: true
  jail_options:
    backend: systemd
fail2ban_manage_epel: true
```

## Example Playbook

```yaml
- name: Apply fail2ban
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.fail2ban
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
