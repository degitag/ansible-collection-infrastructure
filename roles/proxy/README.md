# proxy

Configure proxy environment files for system tools.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Normalizes backslashes and special characters in URL credentials without double-encoding existing percent escapes. Exposes proxy_environment for Ansible task environments; login environment files do not update an already-running Ansible process. Manages only the global proxy key in /etc/pip.conf and preserves other pip settings. Empty input removes the managed pip proxy setting. HTTP(S)/ALL_PROXY and NO_PROXY are emitted in both cases. Explicit pip proxy configuration does not provide a separate per-host bypass setting; use a task environment and proxy_manage_pip: false when NO_PROXY behavior is required. Secrets remain in root-owned tool configuration readable by their users; task output is suppressed.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
proxy_manage_pip: true
```

## Example Playbook

```yaml
- name: Apply proxy
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.proxy
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
