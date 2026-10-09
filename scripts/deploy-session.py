#!/usr/bin/env python3
"""Interactive sudo session; extra vars live in an unlinked file descriptor."""
from pathlib import Path
import getpass, json, shlex, subprocess, tempfile, sys
root = Path(__file__).resolve().parent.parent
commands = {
    'deploy': ['site.yml'],
    'backup': ['backup.yml'],
    'restore': ['restore.yml'],
    'verify': ['site.yml', '--tags', 'verify'],
    'smoke': ['smoke.yml'],
}
secret = getpass.getpass('Sudo password for server@teteo (held only for this session): ')
try:
    with tempfile.TemporaryFile(mode='w+', dir=root / '.local') as variables:
        json.dump({'ansible_become_password': secret}, variables)
        variables.flush()
        secret = None
        def run(parts):
            variables.seek(0)
            return subprocess.run(
                [str(root / '.venv/bin/ansible-playbook'), *commands[parts[0]], *parts[1:],
                 '-e', '@/dev/fd/' + str(variables.fileno())],
                pass_fds=(variables.fileno(),), cwd=root / 'ansible',
            ).returncode
        print('Running deployment; this session can retry after fixes without another password.')
        print('Commands: deploy [Ansible options], smoke, backup, restore, verify, exit')
        print('Deployment exit code:', run(['deploy']))
        while True:
            parts = shlex.split(input('teteo> '))
            if not parts: continue
            if parts[0] == 'exit': break
            if parts[0] not in commands:
                print('Commands:', ', '.join(commands), 'exit'); continue
            print('Command exit code:', run(parts))
except (KeyboardInterrupt, EOFError):
    print('\nSession closed; sudo credentials discarded.')
