# resolvconf

Manage resolver nameservers and search domains.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Static resolv.conf ownership is opt-in via resolvconf_manage_config and requires explicit resolver addresses. Keep it disabled when DHCP, NetworkManager or systemd-resolved owns DNS. Bind-mounted container resolver files additionally require an explicit resolvconf_unsafe_writes opt-in.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
resolvconf_manage_systemd_resolved: true
resolvconf_nameservers: []
resolvconf_search_domains: []
resolvconf_manage_config: false
resolvconf_unsafe_writes: false
```

## Example Playbook

```yaml
- name: Apply resolvconf
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.resolvconf
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
