# dante

Install and configure the Dante SOCKS proxy service.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Debian 13 is explicitly excluded because its stable repositories do not provide dante-server or dante-client. The preflight rejects Debian 13 before mutation. Ubuntu and EL9 use their packaged server and native validator. On Rocky/RHEL 9, the role enables the signed Fedora EPEL 9 repository through dnf_repos by default; set dante_manage_epel: false to use an operator-provided package source. RHEL requires valid base/AppStream repositories and any applicable CodeReady Builder entitlement.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
dante_manage_service: true
dante_service_enabled: true
dante_service_state: started
dante_manage_firewall: false
dante_firewall_zone: public
dante_manage_selinux: true
dante_listen_address: 0.0.0.0
dante_listen_port: 1080
dante_listen_address_ipv6: '::'
dante_enable_ipv6: true
dante_selinux_ports:
- '{{ dante_listen_port }}/tcp'
dante_external_interface: "{{ ansible_facts.default_ipv4.interface | default('') }}"
dante_user: sockd
dante_group: sockd
dante_log_directory: /var/log/sockd
dante_pid_directory: /run/sockd
dante_client_method: none
dante_socks_method: none
dante_client_rules: []
dante_socks_rules: []
dante_manage_epel: true
```

## Example Playbook

```yaml
- name: Apply dante
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.dante
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
