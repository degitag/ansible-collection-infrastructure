from pathlib import Path
import re
import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[2]


def test_defaults_can_be_validated_before_facts_and_do_not_request_certificates():
    defaults = yaml.safe_load((ROOT / 'roles/nginx/defaults/main.yml').read_text())
    env = Environment(undefined=StrictUndefined)
    assert env.from_string(defaults['nginx_worker_processes']).render(ansible_facts={}) == '1'
    certbot = yaml.safe_load((ROOT / 'roles/certbot/defaults/main.yml').read_text())
    assert certbot['certbot_certs'] == []


def test_cloudflare_secret_derivation_is_sequential_and_hidden():
    tasks = yaml.safe_load((ROOT / 'roles/certbot/tasks/configuration.yml').read_text())
    derivations = [t for t in tasks if any(k.startswith('certbot_cloudflare_api_') for k in t.get('ansible.builtin.set_fact', {}))]
    env = Environment(undefined=StrictUndefined)
    env.tests['match'] = lambda value, pattern: re.match(pattern, value) is not None
    for token, key, expected_token, expected_key in [('test-token', '', 'test-token', ''), ('', 'a' * 37, '', 'a' * 37), ('', 'test-scoped-key', 'test-scoped-key', '')]:
        variables = dict(certbot_cloudflare_api_token=token, certbot_cloudflare_api_key=key)
        for task in derivations:
            assert task['no_log'] is True
            values = {name: env.from_string(expression).render(**variables).strip() for name, expression in task['ansible.builtin.set_fact'].items()}
            variables.update(values)
        assert variables['certbot_cloudflare_api_token_effective'] == expected_token
        assert variables['certbot_cloudflare_api_key_effective'] == expected_key
