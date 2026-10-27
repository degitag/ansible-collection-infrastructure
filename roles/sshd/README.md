# sshd

Configure OpenSSH client and server settings.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Prefers modern AEAD ciphers; AES-CTR remains for compatible clients. EL9 uses an AES-only platform list to avoid advertising ChaCha20 in FIPS environments; this is not a compliance certification. Override sshd_server_* inputs deliberately when site crypto policy differs. Ubuntu SSH socket activation is disabled for custom ports when sshd_disable_socket_activation is true and service management is enabled. Existing Match exceptions belong in sshd_server_match_blocks; no UKHD accounts are hard-coded.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
sshd_manage_service: true
sshd_service_enabled: true
sshd_service_state: started
sshd_manage_firewall: false
sshd_firewall_zone: public
sshd_manage_selinux: true
sshd_bind_ips: false
sshd_client_defaults:
  ForwardX11Trusted: true
  GSSAPIAuthentication: true
  SendEnv:
  - LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
  - LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
  - LC_IDENTIFICATION LC_ALL LANGUAGE
  - XMODIFIERS
sshd_client_group_vars: {}
sshd_client_host_vars: {}
sshd_client_playbook: {}
sshd_server_defaults:
  AcceptEnv:
  - LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
  - LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
  - LC_IDENTIFICATION LC_ALL LANGUAGE
  - XMODIFIERS
  AddressFamily: any
  ChallengeResponseAuthentication: false
  GSSAPIAuthentication: true
  GSSAPICleanupCredentials: false
  HostKey:
  - /etc/ssh/ssh_host_ed25519_key
  - /etc/ssh/ssh_host_ecdsa_key
  - /etc/ssh/ssh_host_rsa_key
  PasswordAuthentication: "no"
  PermitRootLogin: "no"
  PermitEmptyPasswords: "no"
  Port: 22
  Protocol: 2
  LoginGraceTime: 30
  StrictModes: "yes"
  MaxStartups: 200
  Subsystem: sftp internal-sftp
  SyslogFacility: AUTHPRIV
  UsePAM: true
  X11Forwarding: true
  PrintMotd: "yes"
  PrintLastLog: "yes"
  Ciphers: "{{ _sshd_default_ciphers | default('chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr') }}"
  MACs: hmac-sha2-256,hmac-sha2-512
  KexAlgorithms: "{{ _sshd_default_kex | default('curve25519-sha256') }}"
  PermitUserEnvironment: "no"
  MaxSessions: 10
  TCPKeepAlive: "yes"
  ClientAliveInterval: 300
  ClientAliveCountMax: 2
sshd_server_group_vars: {}
sshd_server_host_vars: {}
sshd_server_playbook: {}
sshd_server_match_blocks: []
sshd_disable_socket_activation: true
```

## Example Playbook

```yaml
- name: Apply sshd
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.infrastructure.sshd
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
