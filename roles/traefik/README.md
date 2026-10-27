# traefik

Install and configure Traefik reverse proxies and routing rules.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Uses the pinned Traefik v3 release and verifies the upstream archive checksum. Static configuration changes restart the service. Dynamic files use the file provider watcher; if watching is disabled, their changes trigger a restart. No unsupported systemd reload action is invoked.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
traefik_version: 3.7.15
traefik_binary_install_dir: /usr/local/bin
traefik_binary_path: '{{ traefik_binary_install_dir }}/traefik'
traefik_limit_nofile: 16384
traefik_service_name: traefik
traefik_manage_service: true
traefik_service_enabled: true
traefik_service_state: started
traefik_manage_firewall: false
traefik_firewall_zone: public
traefik_manage_selinux: true
traefik_firewall_ports:
- 80/tcp
- 443/tcp
traefik_selinux_ports: '{{ traefik_firewall_ports }}'
traefik_user: traefik
traefik_group: traefik
traefik_external_domain: ''
traefik_acme_email: ''
traefik_http_proxy: ''
traefik_https_proxy: ''
traefik_rules_files: []
traefik_custom_cert_files: []
traefik_config:
  global:
    checkNewVersion: false
    sendAnonymousUsage: false
  api:
    insecure: false
    dashboard: true
  log:
    level: WARN
  entryPoints:
    http:
      address: :80
    https:
      address: :443
  providers:
    file:
      directory: /etc/traefik/rules
      watch: true
traefik_rules_config: {}
```

## Example Playbook

```yaml
- name: Apply traefik
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.traefik
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
