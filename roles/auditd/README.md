# auditd

Manage additional auditd rules.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Installs the native audit package and manages its session rule file. Existing kernel rules are not globally reset unless auditd_reset_existing_rules is explicitly enabled. Extra rules are rendered deterministically and removed when absent from input. EL9 uses the supported service auditd control path. Default rules and extra rules use owned degit-* keys; only those keys are replaced on reload. Additional rules must carry a degit-* key. Unrelated audit rules are preserved. Legacy unprefixed keys disappear at the next reboot or an explicitly requested full reset. Command and session rule groups can be disabled independently. Explicit auditd_remove_legacy_shell_rules migrates the old UKHD logging.rules file and shell_history execve keys. Active removal is scoped to owned execve keys; locked rules fail visibly and require an operator-controlled reboot. It never reboots or resets unrelated rules.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
auditd_manage_service: true
auditd_service_enabled: true
auditd_service_state: started
auditd_extra_rules: []
auditd_reset_existing_rules: false
auditd_shell_commands_enabled: true
auditd_session_logging_enabled: true
auditd_remove_legacy_shell_rules: false
```

## Example Playbook

```yaml
- name: Apply auditd
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.auditd
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
