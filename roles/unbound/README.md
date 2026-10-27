# unbound

Install and configure the Unbound DNS resolver and local zones.

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
unbound_use_blocklist: false
unbound_blocklist_url: https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
unbound_manage_service: true
unbound_service_enabled: true
unbound_service_state: started
unbound_manage_firewall: false
unbound_firewall_zone: public
unbound_manage_selinux: true
unbound_service_name: unbound
unbound_group: unbound
unbound_config_dir: /etc/unbound
unbound_config_path: /etc/unbound/unbound.conf
unbound_root_hints_path: /etc/unbound/root.hints
unbound_local_zones_path: /etc/unbound/local-zones.conf
unbound_blocklist_path: /etc/unbound/unbound.block.conf
unbound_tls_cert_bundle: /etc/ssl/certs/ca-certificates.crt
unbound_checkconf_binary: /usr/sbin/unbound-checkconf
unbound_zones_dir: '{{ unbound_config_dir }}/zones.d'
unbound_local_zones: []
unbound_stub_zones: []
unbound_forward_zones: []
unbound_auth_zones: []
unbound_config:
  server:
    verbosity: 1
    num-threads: '{{ ansible_facts.processor_vcpus | default(ansible_facts.processor_count | default(1)) }}'
    root-hints: '{{ unbound_root_hints_path }}'
    tls-cert-bundle: '{{ unbound_tls_cert_bundle }}'
    log-queries: true
    port: 53
    prefetch: true
    hide-identity: true
    hide-version: true
    do-daemonize: true
    interface:
    - 0.0.0.0
    - ::0
    access-control:
    - 127.0.0.0/8 allow
    - ::1/128 allow
  remote-control:
    control-enable: false
```

## Example Playbook

```yaml
- name: Apply unbound
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.unbound
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
