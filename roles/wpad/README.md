# wpad

Manage a proxy auto-configuration file and publish it through Apache or NGINX.

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
proxy_env: {}
wpad_state: present
wpad_webserver: nginx
wpad_manage_webserver_config: true
wpad_manage_service: true
wpad_service_enabled: true
wpad_service_state: started
wpad_manage_firewall: false
wpad_firewall_zone: public
wpad_manage_selinux: true
wpad_document_root: /var/www/wpad
wpad_pac_filename: proxy.pac
wpad_enable_wpad_dat: true
wpad_server_names:
- wpad
- proxy
wpad_listen_port: 80
wpad_listen_ipv6: true
wpad_cache_control_header: public, max-age=300
wpad_return_string: ''
wpad_proxy_targets: []
wpad_direct_fallback: true
wpad_bypass_plain_hostnames: true
wpad_bypass_localhost: true
wpad_bypass_exact_hosts:
- localhost
- 127.0.0.1
- ::1
wpad_bypass_domain_suffixes:
- .local
- .localdomain
wpad_bypass_host_globs: []
wpad_bypass_networks: []
wpad_custom_rules: []
wpad_extra_pac_logic: ''
```

## Example Playbook

```yaml
- name: Apply wpad
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.wpad
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
