from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_sftp_keys_have_real_line_breaks_and_deduplicate():
    tasks = yaml.safe_load((ROOT / 'roles/sftp_server/tasks/manage_user.yml').read_text())
    expression = next(t['ansible.builtin.copy']['content'] for t in tasks if t.get('name') == 'Install isolated root-owned keys for the SFTP account')
    result = Environment().from_string(expression).render(sftp_server_user={'authorized_keys': ['KEY1', 'KEY2', 'KEY1']})
    assert result == 'KEY1\nKEY2\n'


def test_sftp_uses_account_specific_root_managed_keys_outside_chroot():
    template = Environment(loader=FileSystemLoader(str(ROOT / 'roles/sftp_server/templates'))).get_template('sftp-match.conf.j2')
    rendered = template.render(sftp_server_users=[], sftp_server_group='sftp', sftp_server_base_path='/srv/sftp', sftp_server_authorized_keys_dir='/etc/ssh/authorized_keys', sftp_server_internal_sftp_options=[], sftp_server_allow_password_auth=False, sftp_server_allow_public_key_auth=True)
    assert 'AuthorizedKeysFile /etc/ssh/authorized_keys/%u' in rendered
    assert 'ChrootDirectory /srv/sftp/%u' in rendered
