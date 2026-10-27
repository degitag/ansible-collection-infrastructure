# haproxy

Install and configure HAProxy load balancers and TLS assets.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

With no listeners/frontends configured, the default leaves the service stopped and disabled. Define frontends or listens before enabling traffic. Configuration is validated by the native HAProxy binary.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
haproxy_package_name: haproxy
haproxy_service_name: haproxy
haproxy_manage_service: true
haproxy_service_enabled: '{{ (haproxy_frontends_list | length > 0) or (haproxy_listens_list | length > 0) }}'
haproxy_service_state: "{{ 'started' if ((haproxy_frontends_list | length > 0) or (haproxy_listens_list | length > 0)) else 'stopped' }}"
haproxy_server_user: haproxy
haproxy_server_group: haproxy
haproxy_server_fqdns: []
haproxy_server_tls_certs_dir: /etc/haproxy/certs
haproxy_server_tls_crt_list_path: /etc/haproxy/crt-list.txt
haproxy_manage_letsencrypt_certs: true
haproxy_manage_firewall: false
haproxy_firewall_zone: public
haproxy_manage_selinux: true
haproxy_firewall_ports:
- 80/tcp
- 443/tcp
haproxy_selinux_ports: '{{ haproxy_firewall_ports }}'
haproxy_frontends_list: []
haproxy_backends_list: []
haproxy_listens_list: []
haproxy_userlists_list: []
haproxy_global_config:
  log:
  - /dev/log local0
  - /dev/log local1 notice
  user: '{{ haproxy_server_user }}'
  group: '{{ haproxy_server_group }}'
  daemon: true
haproxy_defaults_config:
  log: global
  mode: http
  option:
  - httplog
  - dontlognull
  timeout:
    connect: 5s
    client: 50s
    server: 50s
```

## Example Playbook

```yaml
- name: Apply haproxy
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.haproxy
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
