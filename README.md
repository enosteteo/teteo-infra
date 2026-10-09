# teteo-infra
Rebuildable homeserver engineering stack. Ansible runs on the Mac via SSH to `server@10.0.0.109`.

## Run
```sh
mise exec python -- python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/init-secrets.py
cd ansible
../.venv/bin/ansible-galaxy collection install -r collections/requirements.yml
../.venv/bin/ansible-playbook site.yml --syntax-check
../.venv/bin/ansible-playbook site.yml --ask-become-pass
```
Phase tags: `check`, `fase1`, `fase3`, `verify`. Phase 2 remains undecided.
A second run must report no unexpected changes. Secrets live in encrypted `ansible/host_vars/teteo.yml`; the ignored Vault key is `.local/vault-password`. Save both to a password manager / independent secure destination for disaster recovery. The local key is a convenience for this Mac, not a second backup.
Read credentials locally with `.venv/bin/ansible-vault view ansible/host_vars/teteo.yml --vault-password-file .local/vault-password`.

## LAN access
DNS must resolve `git`, `s3`, `minio`, `pb`, `backup`, `checks`, `watch`, `buttons`, `jobs` under `teteo.lan` to `10.0.0.109`.
Caddy issues an internal CA. Downloaded certificate: `.local/teteo-root.crt`; trust it explicitly in the client keychain to avoid browser warnings. SSH Git uses port 2222:
```sh
git clone ssh://git@git.teteo.lan:2222/enosteteo/smoke.git
```
Forgejo admin: `teteoadmin`, organization: `enosteteo`. PocketBase admin: `admin@teteo.lan` at `https://pb.teteo.lan/_/`.
Backrest and maintenance UIs are protected; credentials are in the Vault.

## Backup and restore
```sh
cd ansible
../.venv/bin/ansible-playbook backup.yml -K
../.venv/bin/ansible-playbook restore.yml -K
```
Backup briefly stops Forgejo and PocketBase, takes read-only Btrfs snapshots, restarts services, then uploads to a least-privilege MinIO account. Retention: 7 daily, 4 weekly, 6 monthly. MinIO is excluded from its own backup. Restore tests use a new scratch directory and run `git fsck` plus `restic check`; scratch is retained for review.
Backrest imports the same repository for browsing/restoring; schedules are disabled so maintenance never competes with Dagu.
The local MinIO lives on the same disk: off-host replication is still required for disk failure protection.

## Version sources and deviations
- Forgejo 15.0.9 LTS and runner 13.0.0: https://forgejo.org/docs/latest/admin/actions/registration/
- PocketBase 0.40.4: official release binary, SHA256 verified; upstream has no official Docker image: https://pocketbase.io/docs/going-to-production/
- MinIO RELEASE.2025-10-15T17-29-55Z is built from official source to include the last published security fix; upstream is archived: https://github.com/minio/minio/releases/tag/RELEASE.2025-10-15T17-29-55Z
- Ubuntu packages supply Docker/Compose/restic; overlay2 is explicit, Docker data is excluded from backup.
Preserve `/srv/ai-memory`, `/srv/projects` and existing snapshots. No filesystem reformats.
