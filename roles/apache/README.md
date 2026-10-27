# apache

Install and configure Apache HTTP Server and virtual hosts.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
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
apache_additional_packages: []
apache_manage_service: true
apache_service_enabled: true
apache_service_state: started
apache_manage_firewall: false
apache_firewall_zone: public
apache_manage_selinux: true
apache_ports:
- 80
apache_ssl_ports:
- 443
apache_gnutls_ports:
- 443
apache_mods: {}
apache_conf: {}
apache_mpm: prefork
apache_prefork_server_limit: 256
apache_prefork_start_servers: 5
apache_prefork_min_spare_servers: 5
apache_prefork_max_spare_servers: 10
apache_prefork_max_request_workers: 256
apache_prefork_max_connections_per_child: 10000
apache_worker_server_limit: 16
apache_worker_start_servers: 3
apache_worker_min_spare_threads: 75
apache_worker_max_spare_threads: 250
apache_worker_thread_limit: 64
apache_worker_threads_per_child: 25
apache_worker_max_clients: 400
apache_worker_max_connections_per_child: 10000
apache_event_server_limit: 16
apache_event_start_servers: 3
apache_event_min_spare_threads: 75
apache_event_max_spare_threads: 250
apache_event_thread_limit: 64
apache_event_threads_per_child: 25
apache_event_max_clients: 400
apache_event_max_connections_per_child: 10000
apache_remoteip: true
apache_remoteip_header: X-Forwarded-For
apache_remoteip_internal_proxies:
- 127.0.0.1
apache_remoteip_trusted_proxies: []
apache_ssl_protocol: -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
apache_ssl_ciphersuite: ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA
apache_ssl_honorcipherorder: "on"
apache_ssl_compression: "off"
apache_ssl_usestapling: "on"
apache_ssl_staplingcache: 128000
apache_ssl_staplingrespondertimeout: 5
apache_ssl_staplingreturnrespondererrors: "off"
apache_ssl_sessioncache: 512000
apache_ssl_sessioncachetimeout: 300
apache_ssl_headers: []
apache_server_tokens: Prod
apache_server_signature: "Off"
apache_trace_enable: "off"
apache_hostname_lookups: "Off"
apache_listen_backlog: 1024
apache_keepalive: "Off"
apache_keepalive_timeout: 3
apache_max_keepalive_requests: 100
apache_timeout: 300
apache_umask: '022'
apache_user: ''
apache_group: ''
apache_custom_options: {}
apache_mailadmin: admin@example.com
apache_logs_directory: /var/log/{{ _apache_package_name | default('apache') }}/vhosts
apache_logrotate_permissions: '644'
apache_logrotate_user: root
apache_logrotate_group: root
apache_logrotate_retention: '365'
apache_logrotate_frequency: daily
apache_logrotate_paths:
- /var/log/{{ _apache_package_name }}/*.log
- /var/log/{{ _apache_package_name }}/vhosts/*/*.log
apache_logrotate_delay_compress: false
apache_remove_default_vhost: false
apache_default_vhost_template: sites-available/default_vhost.j2
apache_default_vhost_path: /var/www/html
apache_default_vhost_http: true
apache_default_vhost_ssl: false
apache_default_vhost_ssl_certs_path: /etc/{{ _apache_package_name | default('apache') }}/ssl
apache_default_vhost_crt: ''
apache_default_vhost_key: ''
apache_default_vhost_chain: ''
apache_default_vhost_ip: '*'
apache_default_vhost_http_port: 80
apache_default_vhost_ssl_port: 443
apache_vhosts_user: ''
apache_vhosts_group: ''
apache_vhosts_directory: /srv/www
apache_vhosts: []
apache_vhosts_default:
  docroot: current
  create_path: true
  create_docroot: false
  https_redir: false
  https: false
apache_certbot_webroot: /var/www/letsencrypt
apache_default_maintenance_whitelist:
- 127.0.0.0/8
apache_default_maintenance_template: default_maintenance.html.j2
apache_systemd_base_path: /etc/systemd/system
apache_manage_systemd_override: false
apache_systemd_unit_template: ''
```

## Example Playbook

```yaml
- name: Apply apache
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.apache
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
