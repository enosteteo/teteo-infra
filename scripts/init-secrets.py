#!/usr/bin/env python3
from pathlib import Path
import secrets, subprocess, os
import yaml, bcrypt
root=Path(__file__).resolve().parent.parent
os.umask(0o077)
local=root/'.local'; local.mkdir(mode=0o700,exist_ok=True)
key=local/'vault-password'
if not key.exists(): key.write_text(secrets.token_urlsafe(48)+'\n')
host=root/'ansible/host_vars/teteo.yml'
if host.exists(): raise SystemExit('Existing Vault preserved')
ui=secrets.token_urlsafe(32)
data={
 'teteo_minio_root_user':'teteoadmin',
 'teteo_minio_root_password':secrets.token_urlsafe(32),
 'teteo_restic_user':'restic',
 'teteo_restic_key':secrets.token_urlsafe(32),
 'teteo_restic_password':secrets.token_urlsafe(48),
 'teteo_admin_password':secrets.token_urlsafe(32),
 'teteo_ui_password':ui,
 'teteo_ui_password_hash':bcrypt.hashpw(ui.encode(),bcrypt.gensalt()).decode(),
 'teteo_runner_secret':secrets.token_hex(20),
 'teteo_healthchecks_secret':secrets.token_urlsafe(48),
}
subprocess.run([str(root/'.venv/bin/ansible-vault'),'encrypt','--vault-password-file',str(key),'--output',str(host)],input=yaml.safe_dump(data).encode(),check=True,cwd=root)
print('Created encrypted host variables and local Vault key (both ignored by Git)')
