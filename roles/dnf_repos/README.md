# dnf_repos

Manage YUM and DNF repository definitions and signing keys on EL systems.

## Supported platforms

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
dnf_repos_directory: /etc/yum.repos.d
dnf_repos_key_directory: /etc/pki/rpm-gpg
dnf_repos_manage_keys: true
dnf_repos_remove_original: false
dnf_repos_list: []
dnf_repos_manage_epel: false
```

## Example Playbook

```yaml
- name: Configure custom EL repositories
  hosts: el_hosts
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.dnf_repos
      vars:
        dnf_repos_list:
          - name: epel
            description: Extra Packages for Enterprise Linux 9
            metalink: https://mirrors.fedoraproject.org/metalink?repo=epel-9&arch=$basearch
            gpgcheck: true
            gpgkey_url: https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-9
          - name: internal-base
            description: Internal Base Repository
            baseurl: https://repo.example.com/el9/baseos/$basearch
            enabled: true
            gpgcheck: true
            key_path: /etc/pki/rpm-gpg/RPM-GPG-KEY-internal-base
            gpgkey_url: https://repo.example.com/keys/RPM-GPG-KEY-internal-base
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
