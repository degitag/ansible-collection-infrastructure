# nginx

Install and configure NGINX and virtual hosts.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Supports TCP/UDP stream upstreams, maps and servers in addition to HTTP. Installs and loads the distribution stream module only when stream declarations are configured. Set nginx_manage_stream_module: false for an external/static module source and configure nginx_extra_conf_options as required. The complete configuration is validated with nginx -t before restart.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
nginx_default_release: ''
nginx_yum_repo_enabled: true
nginx_zypper_repo_enabled: true
nginx_ppa_use: false
nginx_ppa_version: stable
nginx_package_name: nginx
nginx_manage_service: true
nginx_service_state: started
nginx_service_enabled: true
nginx_manage_firewall: false
nginx_firewall_zone: public
nginx_manage_selinux: true
nginx_firewall_ports:
- 80/tcp
- 443/tcp
nginx_conf_template: nginx.conf.j2
nginx_vhost_template: vhost.j2
nginx_worker_processes: '{{ ansible_facts.processor_vcpus | default(ansible_facts.processor_count | default(1)) }}'
nginx_worker_connections: '1024'
nginx_multi_accept: "off"
nginx_error_log: /var/log/nginx/error.log warn
nginx_access_log: /var/log/nginx/access.log main buffer=16k flush=2m
nginx_sendfile: "on"
nginx_tcp_nopush: "on"
nginx_tcp_nodelay: "on"
nginx_keepalive_timeout: '75'
nginx_keepalive_requests: '600'
nginx_server_tokens: "on"
nginx_client_max_body_size: 64m
nginx_server_names_hash_bucket_size: '64'
nginx_proxy_cache_path: ''
nginx_extra_conf_options: ''
nginx_extra_http_options: ''
nginx_remove_default_vhost: false
nginx_listen_ipv6: true
nginx_vhosts: []
nginx_upstreams: []
nginx_log_format: "'$remote_addr - $remote_user [$time_local] \"$request\" '\n'$status $body_bytes_sent \"$http_referer\" '\n'\"$http_user_agent\" \"$http_x_forwarded_for\"'"
nginx_streams: []
nginx_stream_upstreams: []
nginx_stream_maps: []
nginx_stream_servers: []
nginx_extra_packages: []
nginx_manage_stream_module: true
```

## Example Playbook

```yaml
- name: Apply nginx
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.nginx
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
