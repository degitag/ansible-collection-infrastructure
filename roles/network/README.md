# network

Translate a common network API to Netplan, ifupdown or NetworkManager.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Ubuntu defaults to Netplan/networkd, Debian to ifupdown and Rocky/RHEL to NetworkManager. Supported interface types: ethernet, VLAN, bridge and bond; IPv4/IPv6, DHCP, DNS, gateways and static routes. Empty input does nothing. Only the managed fragment/profiles are owned; existing external files are never wiped. Render and validate first, then explicitly set network_apply: true. This does not disable existing managers or migrate a live management interface automatically. With network_apply: false, NetworkManager uses native module check mode and does not persist or activate profiles; Netplan and ifupdown write validated fragments. Use a console for activation. Interrupted runs are reconciled from current interface state. Existing active NetworkManager profiles for declared interfaces are reused rather than creating competing profiles.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
network_backend: auto
network_interfaces: []
network_apply: false
network_allow_backend_migration: false
network_manage_service: true
network_profile_name: host
```

## Example Playbook

```yaml
- name: Render portable network configuration
  hosts: servers
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.network
      vars:
        network_apply: false
        network_interfaces:
          - name: ens18
            addresses4: [192.0.2.10/24]
            gateway4: 192.0.2.1
            dns: [192.0.2.53]
            search: [example.net]
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
