# firewall

Manage a common firewall rule API through UFW or firewalld.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

The portable API manages inbound TCP/UDP port rules, optional source/destination CIDRs and allow/deny/reject actions. Rules are additive; remove an owned rule explicitly with state: absent. A service role only adds its own rules and never resets the host policy. UFW activation is opt-in via firewall_manage_activation. firewalld needs a running daemon for immediate rules. Zone selection is firewalld-specific; interface matching is UFW-specific. Do not assume an interface filter is translated into a zone. The default incoming policy currently applies to UFW only. firewall_trusted_sources explicitly trusts entire CIDRs, including forwarding; use only for private pod/service networks. Trust assignments are additive and require explicit native removal when decommissioned.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
firewall_backend: auto
firewall_manage_service: true
firewall_service_enabled: true
firewall_service_state: started
firewall_manage_activation: false
firewall_enabled: true
firewall_default_incoming_policy: deny
firewall_zone: public
firewall_rules: []
firewall_trusted_sources: []
```

## Example Playbook

```yaml
- name: Configure host firewall
  hosts: servers
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.firewall
      vars:
        firewall_rules:
          - port: '22'
            protocol: tcp
            source: 192.0.2.0/24
            comment: Administration
          - port: '443'
            protocol: tcp
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
