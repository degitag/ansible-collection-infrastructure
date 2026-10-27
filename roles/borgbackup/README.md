# borgbackup

Install and configure BorgBackup jobs and defaults.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

 On Rocky/RHEL 9, the role enables the signed Fedora EPEL 9 repository through dnf_repos by default; set borgbackup_manage_epel: false to use an operator-provided package source. RHEL requires valid base/AppStream repositories and any applicable CodeReady Builder entitlement. Local repository initialization and cron scheduling are opt-in. Encrypted repositories require an explicit passphrase; repository and script permissions restrict access to root. Archive timestamps are evaluated by Borg at backup time.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
borgbackup_repository: /var/backups/borg
borgbackup_source_paths:
- /etc
borgbackup_archive_name: '{now:%Y-%m-%dT%H:%M:%S}'
borgbackup_encryption_mode: repokey
borgbackup_encryption_passphrase: ''
borgbackup_keep_daily: 7
borgbackup_keep_weekly: 4
borgbackup_keep_monthly: 6
borgbackup_script_path: /usr/local/bin/borgbackup.sh
borgbackup_cron_minute: '0'
borgbackup_cron_hour: '2'
borgbackup_manage_epel: true
borgbackup_manage_repository: false
borgbackup_manage_cron: false
```

## Example Playbook

```yaml
- name: Configure encrypted local backups
  hosts: backup_clients
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.borgbackup
      vars:
        borgbackup_manage_repository: true
        borgbackup_manage_cron: true
        borgbackup_encryption_passphrase: "{{ vault_borg_passphrase }}"
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
