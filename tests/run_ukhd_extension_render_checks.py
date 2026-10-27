#!/usr/bin/env python3
"""Render extension artifacts using real Ansible and the current production tasks."""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]

PLAY = [{'name': 'Render portable extensions without changing the controller',
  'hosts': 'localhost',
  'connection': 'local',
  'gather_facts': False,
  'become': False,
  'vars': {'ansible_managed': 'test artifact',
           'proxy_env': {'http_proxy': 'http://DOMAIN\\user:p%40ss@proxy.invalid:8080',
                         'no_proxy': 'localhost,127.0.0.1'},
           'conditional_reboot_enabled': False,
           'conditional_reboot_time': {'hour': 4, 'minute': 0},
           'conditional_reboot_day_filter_enabled': True,
           'conditional_reboot_day_of_week': 3,
           'conditional_reboot_day_of_month_range': [1, 7],
           'conditional_reboot_window_minutes': 15,
           'conditional_reboot_log_path': '',
           '_conditional_reboot_requirement_file': '/var/run/reboot-required',
           '_conditional_reboot_requirement_command': [],
           '_conditional_reboot_command': ['DO-NOT-EXECUTE'],
           '_conditional_reboot_script': '/usr/local/sbin/reboot-check.py',
           '_conditional_reboot_config': '/etc/conditional-reboot.json'},
  'tasks': [{'name': 'Create temporary render directory',
             'ansible.builtin.tempfile': {'state': 'directory', 'prefix': 'degit-extension-render-'},
             'register': 'render_dir'},
            {'name': 'Render and validate temporary artifacts',
             'block': [{'name': 'Normalize real Ansible proxy values',
                        'ansible.builtin.set_fact': {'_docker_proxy_environment': '{{ proxy_env | '
                                                                                  'degitag.infrastructure.proxy_environment '
                                                                                  '}}'}},
                       {'name': 'Require correct domain separator encoding',
                        'ansible.builtin.assert': {'that': ['_docker_proxy_environment.http_proxy == '
                                                            "'http://DOMAIN%5Cuser:p%40ss@proxy.invalid:8080'"]}},
                       {'name': 'Render systemd proxy twice',
                        'ansible.builtin.template': {'src': '../../roles/docker/templates/http-proxy.conf.j2',
                                                     'dest': '{{ render_dir.path }}/http-proxy.conf',
                                                     'mode': '0600'},
                        'loop': [1, 2],
                        'register': 'proxy_render'},
                       {'name': 'Require idempotent systemd rendering',
                        'ansible.builtin.assert': {'that': ['not proxy_render.results[1].changed']}},
                       {'name': 'Runtime production policy task'},
                       {'name': 'Read rendered policy',
                        'ansible.builtin.slurp': {'src': '{{ render_dir.path }}/policy.json'},
                        'register': 'policy'},
                       {'name': 'Check native policy types',
                        'ansible.builtin.assert': {'that': ['(policy.content | b64decode | '
                                                            'from_json).enabled is sameas false',
                                                            '(policy.content | b64decode | from_json).hour '
                                                            'is integer',
                                                            '(policy.content | b64decode | '
                                                            'from_json).day_of_month_range == [1, 7]']}},
                       {'name': 'Render reboot service with consistent script path',
                        'ansible.builtin.template': {'src': '../../roles/conditional_reboot/templates/reboot-check.service.j2',
                                                     'dest': '{{ render_dir.path }}/reboot-check.service',
                                                     'mode': '0600'}}],
             'always': [{'name': 'Remove temporary render artifacts',
                         'ansible.builtin.file': {'path': '{{ render_dir.path }}', 'state': 'absent'}}]}]}]


def main():
    play = PLAY[0]
    block = play['tasks'][1]['block']
    policy = next(task for task in yaml.safe_load((ROOT / 'roles/conditional_reboot/tasks/configuration.yml').read_text())
                  if task['name'] == 'Write typed reboot policy')
    policy['ansible.builtin.copy'].update(dest='{{ render_dir.path }}/policy.json')
    for key in ('owner', 'group'):
        policy['ansible.builtin.copy'].pop(key, None)
    policy['become'] = False
    block[4] = policy
    for task in block:
        if 'ansible.builtin.template' in task:
            template = task['ansible.builtin.template']
            template['src'] = str(ROOT / template['src'].removeprefix('../../'))
    with tempfile.TemporaryDirectory(prefix='degit-render-test-') as directory:
        path = Path(directory) / 'playbook.yml'
        path.write_text(yaml.safe_dump(PLAY, sort_keys=False))
        subprocess.run(['ansible-playbook', '-i', 'localhost,', str(path)], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
