"""Regression tests for transferred behavior, including actual pip proxy traffic."""
from pathlib import Path
import base64
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ansible.errors import AnsibleFilterError
from jinja2 import Environment, FileSystemLoader
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


proxy = module_at('proxy', 'plugins/filter/proxy.py')
reboot = module_at('reboot', 'roles/conditional_reboot/files/reboot-check.py')


def render(role, filename, **context):
    env = Environment(loader=FileSystemLoader(str(ROOT / 'roles' / role / 'templates')), trim_blocks=True, lstrip_blocks=True)
    env.filters.update(comment=lambda s: '# ' + s, bool=bool, to_json=json.dumps)
    return env.get_template(filename).render(ansible_managed='managed', **context)


@pytest.mark.parametrize('url', [r'http://DOMAIN\user:p%40ss@proxy.invalid:8080', 'http://DOMAIN%5Cuser:p%40ss@proxy.invalid:8080'])
def test_proxy_encodes_domain_separator_exactly_once(url):
    normalized = proxy.proxy_url(url)
    assert normalized == 'http://DOMAIN%5Cuser:p%40ss@proxy.invalid:8080'
    assert proxy.proxy_url(normalized) == normalized


@pytest.mark.parametrize('url', ['http://proxy.invalid:3128', 'http://[2001:db8::1]:3128', 'https://u:p@proxy.invalid/'])
def test_proxy_preserves_valid_unauthenticated_ipv6_and_https(url):
    assert proxy.proxy_url(url) == url


def test_password_delimiters_and_literal_percent_are_encoded():
    assert proxy.proxy_url('http://u:p@ss%word@proxy.invalid') == 'http://u:p%40ss%25word@proxy.invalid'


@pytest.mark.parametrize('url', ['proxy:3128', 'file:///etc/passwd', 'http://x\nInjected=x', 'http://proxy.invalid/#bad', 'http://proxy.invalid:99999'])
def test_invalid_proxy_is_rejected_before_writing_files(url):
    with pytest.raises(AnsibleFilterError):
        proxy.proxy_url(url)


def test_uppercase_environment_and_no_proxy_are_preserved():
    result = proxy.proxy_environment({'HTTPS_PROXY': r'http://D\u:p@proxy.invalid', 'NO_PROXY': '.example.net,127.0.0.1,::1'})
    assert result['HTTPS_PROXY'] == result['https_proxy'] == 'http://D%5Cu:p@proxy.invalid'
    assert result['NO_PROXY'] == result['no_proxy'] == '.example.net,127.0.0.1,::1'


def test_systemd_encoding_round_trips_without_double_encoding_url():
    values = proxy.proxy_environment({'http_proxy': r'http://DOMAIN\user:p%40ss@proxy.invalid'})
    output = render('docker', 'http-proxy.conf.j2', _docker_proxy_environment=values)
    assert 'DOMAIN%%5Cuser:p%%40ss' in output
    for line in output.splitlines():
        if line.startswith('Environment='):
            assignment = json.loads(line.removeprefix('Environment=')).replace('%%', '%')
            key, value = assignment.split('=', 1)
            assert value == values[key]


def policy(tmp_path):
    marker = tmp_path / 'reboot-required'
    marker.touch()
    return dict(enabled=True, hour=4, minute=0, window_minutes=15, day_filter_enabled=True,
                day_of_week=3, day_of_month_range=[1, 7], requirement_file=str(marker),
                requirement_command=[], reboot_command=['DO-NOT-EXECUTE'])


@pytest.mark.parametrize('now,expected', [
    (datetime.datetime(2026, 10, 7, 4, 0), True),
    (datetime.datetime(2026, 10, 7, 4, 14, 59), True),
    (datetime.datetime(2026, 10, 7, 4, 15), False),
    (datetime.datetime(2026, 10, 7, 3, 59), False),
    (datetime.datetime(2026, 10, 14, 4, 0), False),
    (datetime.datetime(2026, 10, 8, 4, 0), False),
])
def test_reboot_window_enforces_first_wednesday_and_bounded_time(tmp_path, now, expected):
    assert reboot.in_window(policy(tmp_path), now) is expected


def test_disabled_policy_never_queries_or_reboots(tmp_path):
    config = policy(tmp_path)
    config['enabled'] = False
    assert reboot.execute(config, run=lambda *a, **k: pytest.fail('must not execute commands')) == 'disabled'


def test_dry_run_and_missing_marker_cannot_reboot(tmp_path):
    config = policy(tmp_path)
    now = datetime.datetime(2026, 10, 7, 4, 0)
    forbidden = lambda *a, **k: pytest.fail('must not reboot')
    assert reboot.execute(config, now, dry_run=True, run=forbidden) == 'reboot required (dry run)'
    Path(config['requirement_file']).unlink()
    assert reboot.execute(config, now, run=forbidden) == 'no reboot required'


@pytest.mark.parametrize('rc,expected', [(0, False), (1, True)])
def test_el9_requirement_exit_codes(tmp_path, rc, expected):
    config = policy(tmp_path)
    config['requirement_file'] = ''
    assert reboot.required(config, run=lambda *a, **k: subprocess.CompletedProcess(a, rc)) is expected


def test_failed_el9_check_never_triggers_reboot(tmp_path):
    config = policy(tmp_path)
    config['requirement_file'] = ''
    calls = []
    def failed(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 2)
    with pytest.raises(RuntimeError):
        reboot.execute(config, datetime.datetime(2026, 10, 7, 4, 0), run=failed)
    assert calls == [config['requirement_command']]


def test_reboot_only_calls_explicit_command_inside_allowed_window(tmp_path):
    config = policy(tmp_path)
    calls = []
    assert reboot.execute(config, datetime.datetime(2026, 10, 7, 4, 0), run=lambda cmd, **kw: calls.append(cmd)) == 'reboot requested'
    assert calls == [['DO-NOT-EXECUTE']]


def test_prompt_does_not_modify_noninteractive_or_posix_shells(tmp_path):
    helper = ROOT / 'roles/prompt/files/git-prompt.sh'
    output = render('prompt', 'prompt.sh.j2', prompt_git_branch=True, _prompt_profile_dir=str(helper.parent))
    script = tmp_path / 'prompt.sh'
    script.write_text(output)
    subprocess.run(['bash', '-n', str(script)], check=True)
    result = subprocess.run(['bash', '-c', 'PS1=original; . "$1"; printf "%s" "$PS1"', 'bash', str(script)], capture_output=True, text=True, check=True)
    assert result.stdout == 'original'
    subprocess.run(['/bin/sh', '-c', '. "$1"', 'sh', str(script)], check=True)
    interactive = subprocess.run(['bash', '--noprofile', '--norc', '-ic', '. "$1"; declare -F parse_git_branch; printf "%s" "$PS1"', 'bash', str(script)], capture_output=True, text=True, check=True)
    assert 'parse_git_branch' in interactive.stdout
    assert '$(parse_git_branch)' in interactive.stdout


def test_audit_shell_rule_disable_preserves_session_events():
    output = render('auditd', 'audit.rules.j2', auditd_reset_existing_rules=False, _auditd_extra_keys=[],
                    auditd_shell_commands_enabled=False, auditd_session_logging_enabled=True,
                    auditd_extra_rules=[], ansible_facts={'architecture':'x86_64'})
    assert '-S execve' not in output
    assert '-w /var/log/wtmp' in output
    assert '-D -k degit-user-cmd' in output
    assert '\n-D\n' not in output


def test_real_pip_download_uses_encoded_proxy_credentials(tmp_path):
    wheel = io.BytesIO()
    with zipfile.ZipFile(wheel, 'w') as archive:
        archive.writestr('demo-1.0.dist-info/METADATA', 'Metadata-Version: 2.1\nName: demo\nVersion: 1.0\n')
        archive.writestr('demo-1.0.dist-info/WHEEL', 'Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n')
        archive.writestr('demo-1.0.dist-info/RECORD', '')
    observed = []
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            observed.append((self.path, self.headers.get('Proxy-Authorization')))
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(len(wheel.getvalue())))
            self.end_headers()
            self.wfile.write(wheel.getvalue())
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = proxy.proxy_url(r'http://DOMAIN\user:p%40ss@127.0.0.1:' + str(server.server_port))
        config = tmp_path / 'pip.conf'
        config.write_text('[global]\nproxy = ' + url + '\n')
        env = {k:v for k,v in os.environ.items() if 'proxy' not in k.lower() and not k.startswith('PIP_')}
        env['PIP_CONFIG_FILE'] = str(config)
        result = subprocess.run([sys.executable, '-m', 'pip', 'download', '--disable-pip-version-check', '--no-cache-dir', '--no-deps', '--dest', str(tmp_path), '--trusted-host', 'packages.example.invalid', 'http://packages.example.invalid/demo-1.0-py3-none-any.whl'], env=env, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / 'demo-1.0-py3-none-any.whl').exists()
        assert observed[0][1] == 'Basic ' + base64.b64encode(b'DOMAIN\\user:p@ss').decode()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_native_sshd_accepts_both_platform_cipher_lists(tmp_path):
    import shutil
    sshd = shutil.which('sshd')
    keygen = shutil.which('ssh-keygen')
    if not sshd or not keygen:
        pytest.skip('Native OpenSSH server tools are not installed')
    key = tmp_path / 'hostkey'
    subprocess.run([keygen, '-q', '-t', 'ed25519', '-N', '', '-f', str(key)], check=True)
    defaults = yaml.safe_load((ROOT / 'roles/sshd/defaults/main.yml').read_text())
    for family in ('Debian', 'RedHat'):
        platform = yaml.safe_load((ROOT / f'roles/sshd/vars/platform/{family}.yml').read_text())
        server = dict(defaults['sshd_server_defaults'])
        server.update(Ciphers=platform['_sshd_default_ciphers'], KexAlgorithms=platform['_sshd_default_kex'], HostKey=[str(key)])
        config = tmp_path / (family + '.conf')
        config.write_text(render('sshd', 'sshd.config.j2', sshd_server=server, sshd_bind_ips=False,
                                 sshd_server_match_blocks=[], _sshd_server_include_glob=str(tmp_path / '*.fragment')))
        result = subprocess.run([sshd, '-t', '-f', str(config)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        effective = subprocess.run([sshd, '-T', '-f', str(config)], capture_output=True, text=True, check=True)
        assert 'ciphers ' + platform['_sshd_default_ciphers'] in effective.stdout


def test_docker_all_proxy_fallback_sets_supported_http_variables():
    values = proxy.proxy_environment({'ALL_PROXY': r'http://D\user:p@proxy.invalid'}, fallback_all=True)
    assert values['HTTP_PROXY'] == values['HTTPS_PROXY'] == 'http://D%5Cuser:p@proxy.invalid'
