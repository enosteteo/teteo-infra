# teteo-infra
Ansible runs on the Mac, targeting teteo via SSH. Read README.md before changes.
Keep host variables and credentials out of Git; use Ansible Vault and no_log.
Never reformat storage or replace existing /srv/ai-memory, /srv/projects or snapshots.
Phase 2 is undecided and must not be installed. Pin upstream versions.
Check: cd ansible && ../.venv/bin/ansible-playbook site.yml --syntax-check
Deployment: ../.venv/bin/ansible-playbook site.yml --ask-become-pass
Validate a second run for idempotence and exercise backup/restore before declaring completion.
Never restore into live data; require an explicit scratch destination.
