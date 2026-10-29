# kernel_crash_recovery

Configure persistent automatic reboot after a kernel panic or Oops.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Including this role explicitly enables panic-on-Oops and a 60-second panic reboot delay. It configures recovery; it never deliberately panics or reboots a host. The platform matrix covers Debian 13, Ubuntu LTS and EL9; live acceptance must be recorded per platform. kernel_crash_recovery_panic_timeout accepts 1–3600 seconds. kernel_crash_recovery_apply: false writes the next-boot policy without changing the running kernel; it does not disable the persisted policy. Container tests must use this mode because containers share their host kernel. Live activation in detected containers is rejected. Apply without reboot; reconcile runtime drift even when the fragment already matches. The dedicated root-owned /etc/sysctl.d/90-kernel-crash-recovery.conf owns only kernel.panic and kernel.panic_on_oops. Do not declare these keys in another sysctl role or fragment; a later sysctl.d file or /etc/sysctl.conf may override boot values. WARN, OOM and lockup policies remain outside this role. Keep persistent journal/pstore evidence and unexpected-reboot alerts; kdump and watchdogs need separate coordination. Recovery can lose uncommitted writes and a recurring kernel defect can cause reboot loops. It does not repair a kernel bug or guarantee recovery from every hang. Roll out serially to the test host first, check live values and a second unchanged run, then expand by inventory limit. Do not inject a panic on a shared test server. Rollback: set kernel_crash_recovery_enabled: false and apply with kernel_crash_recovery_apply: true; both persisted and live values become zero. Configuration-only rollback takes effect on the next sysctl load or boot. Removing the role or deleting the fragment alone does not reset running values. Restore any prior custom policy explicitly. Use vim to inspect the fragment when diagnosing drift.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
kernel_crash_recovery_enabled: true
kernel_crash_recovery_panic_timeout: 60
kernel_crash_recovery_apply: true
```

## Example Playbook

```yaml
- name: Configure kernel crash recovery
  hosts: linux_vms
  become: true
  gather_facts: true
  serial: 1
  roles:
    - role: degitag.infrastructure.kernel_crash_recovery
      vars:
        kernel_crash_recovery_enabled: true
        kernel_crash_recovery_panic_timeout: 60
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
