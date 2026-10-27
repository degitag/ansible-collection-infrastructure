"""Run the real key tasks against disposable files and a local HTTP server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_repository_key_idempotence_rotation_and_recovery(tmp_path):
    gpg = shutil.which('gpg')
    if not gpg:
        pytest.skip('GPG is required for the native keyring regression')
    home = tmp_path / 'gnupg'
    home.mkdir(mode=0o700)
    environment = {**os.environ, 'GNUPGHOME': str(home), 'ANSIBLE_HOME': str(tmp_path / 'ansible'),
                   'ANSIBLE_NOCOLOR': '1', 'ANSIBLE_STDOUT_CALLBACK': 'default', 'NO_PROXY': '127.0.0.1,localhost'}
    # Opaque test bytes exercise armoring without generating any private keys.
    def armor(data):
        return subprocess.check_output([gpg, '--batch', '--enarmor'], input=data, env=environment)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Length', str(len(self.server.armored_key)))
            self.end_headers()
            self.wfile.write(self.server.armored_key)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.armored_key = armor(b'first test key material')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    names = {'Install GPG key', 'Inspect the installed Debian repository keyring',
             'Dearmor InfluxData archive key for Debian'}
    source = yaml.safe_load((ROOT / 'roles/telegraf/tasks/configuration.yml').read_text())
    tasks = [task for task in source if task.get('name') in names]
    assert len(tasks) == len(names)
    for task in tasks:
        task.pop('become', None)
    keyring = tmp_path / 'archive.gpg'
    variables = {'ansible_connection': 'local', 'ansible_python_interpreter': sys.executable,
                 'ansible_facts': {'os_family': 'Debian'}, 'telegraf_manage_repository': True,
                 'telegraf_gpg_key_url': f'http://127.0.0.1:{server.server_port}/key',
                 'telegraf_apt_key_download_path': str(tmp_path / 'archive.key'),
                 'telegraf_apt_keyring_path': str(keyring)}

    def run(enabled=True):
        playbook = tmp_path / 'keyring.yml'
        playbook.write_text(yaml.safe_dump([{'name': 'Exercise repository keys', 'hosts': 'localhost',
                                             'gather_facts': False, 'environment': {'GNUPGHOME': str(home)},
                                             'vars': {**variables, 'telegraf_manage_repository': enabled},
                                             'tasks': tasks}], sort_keys=False))
        result = subprocess.run([str(Path(sys.executable).with_name('ansible-playbook')),
                                 '-i', 'localhost,', str(playbook)], env=environment,
                                capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        recap = re.search(r'localhost\s+:\s+ok=\d+\s+changed=(\d+).*?failed=(\d+)', result.stdout)
        assert recap, result.stdout
        assert recap.group(2) == '0'
        return int(recap.group(1))

    try:
        assert run() == 2
        assert keyring.read_bytes() == b'first test key material'
        assert run() == 0
        keyring.unlink()
        assert run() == 1
        assert keyring.read_bytes() == b'first test key material'
        keyring.write_bytes(b'')
        assert run() == 1
        server.armored_key = armor(b'rotated test key material')
        assert run() == 2
        assert keyring.read_bytes() == b'rotated test key material'
        assert run() == 0
        keyring.unlink()
        assert run(enabled=False) == 0
        assert not keyring.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
