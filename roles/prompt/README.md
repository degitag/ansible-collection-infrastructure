# prompt

Configure an interactive Bash prompt and optional operator helpers.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Interactive Bash only. Git prompt helper is included locally; optional SSH agent, root dotfiles, bcrypt and yq are independent explicit choices. yq downloads require a pinned version and SHA256 checksum. The bcrypt helper requires Python bcrypt at runtime. No personal configuration is installed unless requested. Coordinate ownership with users_manage_root_dotfiles and users powerline-go; only one role should own each prompt or dotfile.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
prompt_enabled: true
prompt_manage_ssh_agent: false
prompt_manage_root_dotfiles: false
prompt_install_bcrypt: false
prompt_install_yq: false
prompt_yq_version: 4.44.3
prompt_yq_checksum: ''
prompt_git_branch: true
```

## Example Playbook

```yaml
- name: Configure operator prompt
  hosts: linux_hosts
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.prompt
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
