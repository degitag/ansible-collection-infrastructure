# docker

Install Docker Engine from the official Docker repositories and manage daemon settings.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Docker proxy input defaults to proxy_env, or set docker_proxy_env explicitly. URLs use the shared normalizer. A root-readable systemd drop-in sets both variable cases; percent signs are escaped for systemd. Disabled proxies remove only the owned http-proxy.conf drop-in. Handlers are flushed before the role returns so later image pulls use the new configuration. docker_manage_proxy: false leaves proxy ownership elsewhere; do not mix this drop-in with daemon.json proxies.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
docker_manage_repository: true
docker_remove_conflicting_packages: false
docker_manage_daemon_config: true
docker_manage_service: true
docker_service_enabled: true
docker_service_state: started
docker_users: []
docker_packages:
- docker-ce
- docker-ce-cli
- containerd.io
- docker-buildx-plugin
- docker-compose-plugin
docker_daemon_config: {}
docker_manage_proxy: true
docker_proxy_env: '{{ proxy_env | default({}) }}'
```

## Example Playbook

```yaml
- name: Install and configure Docker Engine
  hosts: container_hosts
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.docker
      vars:
        docker_users:
          - deploy
        docker_daemon_config:
          log-driver: json-file
          log-opts:
            max-size: "10m"
            max-file: "3"
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
