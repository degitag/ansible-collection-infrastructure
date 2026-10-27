# sftp_server

Manage chrooted SFTP-only accounts and SSH match configuration.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

SFTP account homes are paths inside their chroot. Public keys are stored in separate root-owned files under sftp_server_authorized_keys_dir and selected by AuthorizedKeysFile %u; users never share a host-level home key file. The role validates the fragment and complete sshd configuration, ensures the fragment is included, and respects manage_service. On SELinux systems it labels chroots/keys and enables the chroot write boolean for configured users.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
sftp_server_group: sftp
sftp_server_base_path: /srv/sftp
sftp_server_manage_sshd: true
sftp_server_manage_service: true
sftp_server_service_enabled: true
sftp_server_service_state: started
sftp_server_allow_password_auth: false
sftp_server_allow_public_key_auth: true
sftp_server_default_password_lock: true
sftp_server_default_shell: ''
sftp_server_home_subdirectory: data
sftp_server_default_directories:
- data
sftp_server_directory_mode: '0750'
sftp_server_remove_chroot_on_absent: false
sftp_server_internal_sftp_options: []
sftp_server_users: []
sftp_server_authorized_keys_dir: /etc/ssh/authorized_keys
sftp_server_manage_selinux: true
```

## Example Playbook

```yaml
- name: Apply sftp_server
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.sftp_server
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
