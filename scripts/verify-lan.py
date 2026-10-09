#!/usr/bin/env python3
"""Verify LAN HTTPS with the fetched CA, without changing client DNS or trust."""
from pathlib import Path
import subprocess, yaml
root = Path(__file__).resolve().parent.parent
values = yaml.safe_load(subprocess.check_output([
    str(root/'.venv/bin/ansible-vault'), 'view', str(root/'ansible/host_vars/teteo.yml'),
    '--vault-password-file', str(root/'.local/vault-password'),
]))
settings = yaml.safe_load((root/'ansible/group_vars/all/main.yml').read_text())
address = values['ansible_host']
domain = values.get('teteo_domain', settings['teteo_domain'])
user = values.get('teteo_admin_user', settings['teteo_admin_user'])
checks = {
    '': '/',
    'git': '/api/healthz', 'pb': '/api/health', 's3': '/minio/health/live',
    'minio': '/', 'backup': '/', 'checks': '/', 'watch': '/', 'buttons': '/', 'jobs': '/',
}
ca = root/'.local/teteo-root.crt'
if not ca.exists(): raise SystemExit('Fetch the CA with the Ansible verify tag first')
for name, path in checks.items():
    host = (name + '.' if name else '') + domain
    config = '\n'.join([
        f'url = "https://{host}{path}"',
        f'resolve = "{host}:443:{address}"',
        f'cacert = "{ca}"',
        'silent', 'show-error', 'output = "/dev/null"', 'max-time = 20',
        'write-out = "%{http_code}"',
    ]) + '\n'
    if name in ['backup', 'watch', 'buttons', 'jobs']:
        config += f'user = "{user}:{values["teteo_ui_password"]}"\n'
    result = subprocess.run(['curl', '--config', '-'], input=config, capture_output=True, text=True)
    if result.returncode or result.stdout not in ['200', '301', '302', '303']:
        raise SystemExit(f'{host}: TLS/HTTP verification failed (status {result.stdout})')
    print(f'{host}: certificate verified, HTTP {result.stdout}')
