# telegraf

Install and configure Telegraf with plugin definitions.

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
telegraf_manage_repository: true
telegraf_manage_service: true
telegraf_service_enabled: true
telegraf_service_state: started
telegraf_manage_firewall: false
telegraf_firewall_zone: public
telegraf_manage_selinux: true
telegraf_firewall_ports:
- 9273/tcp
telegraf_manage_main_config: true
telegraf_manage_plugin_configs: true
telegraf_apt_repo: deb [signed-by={{ telegraf_apt_keyring_path }}] https://repos.influxdata.com/debian stable main
telegraf_yum_repo_baseurl: https://repos.influxdata.com/rhel/$releasever/$basearch/stable
telegraf_gpg_key_url: https://repos.influxdata.com/influxdata-archive.key
telegraf_apt_keyring_path: /etc/apt/keyrings/influxdata-archive.gpg
telegraf_apt_key_download_path: /etc/apt/keyrings/influxdata-archive.key
telegraf_config_path: /etc/telegraf/telegraf.conf
telegraf_plugins_path: /etc/telegraf/telegraf.d
telegraf_service_name: telegraf
telegraf_package_name: telegraf
telegraf_user: telegraf
telegraf_extra_groups: []
telegraf_extra_groups_group_vars: []
telegraf_extra_groups_host_vars: []
telegraf_extra_groups_playbook: []
telegraf_plugins: []
telegraf_plugins_group_vars: []
telegraf_plugins_host_vars: []
telegraf_plugins_playbook: []
telegraf_plugin_files:
- name: 10-inputs-host-base.conf
  sections:
  - plugin_type: inputs
    type: procstat
    config:
      pid_file: /var/run/sshd.pid
  - plugin_type: inputs
    type: diskio
    config: {}
  - plugin_type: inputs
    type: kernel
    config: {}
  - plugin_type: inputs
    type: processes
    config: {}
  - plugin_type: inputs
    type: netstat
    config: {}
  - plugin_type: inputs
    type: lvm
    config: {}
  - plugin_type: inputs
    type: cgroup
    config:
      paths:
      - /sys/fs/cgroup/cpu,cpuacct/cpuacct.usage
      - /sys/fs/cgroup/cpu,cpuacct/cpuacct.stat
      - /sys/fs/cgroup/memory/memory.usage_in_bytes
      - /sys/fs/cgroup/memory/memory.stat
telegraf_plugin_files_group_vars: []
telegraf_plugin_files_host_vars: []
telegraf_plugin_files_playbook: []
telegraf_global_tags: {}
telegraf_global_tags_group_vars: {}
telegraf_global_tags_host_vars: {}
telegraf_global_tags_playbook: {}
telegraf_config:
  agent:
    interval: 10s
    round_interval: true
    metric_batch_size: 1000
    metric_buffer_limit: 10000
    collection_jitter: 0s
    flush_interval: 10s
    flush_jitter: 0s
    precision: ''
    hostname: '{{ ansible_facts.hostname | default(inventory_hostname) }}'
    omit_hostname: false
  outputs:
  - type: prometheus_client
    config:
      listen: :9273
      metric_version: 2
  inputs:
  - type: cpu
    config:
      percpu: true
      totalcpu: true
      collect_cpu_time: false
      report_active: false
  - type: mem
    config: {}
  - type: disk
    config:
      ignore_fs:
      - tmpfs
      - devtmpfs
      - overlay
      - squashfs
  - type: net
    config: {}
  - type: system
    config: {}
```

## Example Playbook

```yaml
- name: Apply telegraf
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.telegraf
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
