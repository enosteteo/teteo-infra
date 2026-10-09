# teteo-infra
Rebuildable homeserver engineering stack. Ansible runs on the Mac via SSH to `server@<SERVER_IP>`.

## Run
```sh
mise exec python -- python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/init-secrets.py --host <SERVER_IP>
cd ansible
../.venv/bin/ansible-galaxy collection install -r collections/requirements.yml
../.venv/bin/ansible-playbook site.yml --syntax-check
../.venv/bin/ansible-playbook site.yml --ask-become-pass
```
Phase tags: `check`, `fase1`, `fase3`, `verify`. Phase 2 remains undecided.
A second run must report no unexpected changes. Secrets live in encrypted `ansible/host_vars/teteo.yml`; the ignored Vault key is `.local/vault-password`. Save both to a password manager / independent secure destination for disaster recovery. The local key is a convenience for this Mac, not a second backup.
Read credentials locally with `.venv/bin/ansible-vault view ansible/host_vars/teteo.yml --vault-password-file .local/vault-password`.

## LAN access
DNS must resolve `git`, `s3`, `minio`, `pb`, `backup`, `checks`, `watch`, `buttons`, `jobs` under `teteo.lan` to the server IP from encrypted host variables.
Caddy issues an internal CA. Downloaded certificate: `.local/teteo-root.crt`; trust it explicitly in the client keychain to avoid browser warnings. A client hosts/DNS snippet is generated at `.local/teteo.hosts`. You can verify every HTTPS route before configuring client DNS with `.venv/bin/python scripts/verify-lan.py`; it uses the CA file and explicit name resolution without changing macOS settings.
SSH Git uses port 2222:
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

## Phase 3
Healthchecks (SQLite, one worker), changedetection.io and OliveTin run in a separate Compose project. Dagu runs as a systemd service on the host so it can take Btrfs snapshots without a privileged container. Its UI binds only to the Docker host gateway, sits behind Caddy, and requires authentication. OliveTin calls its authenticated API; it has no Docker socket or host volume access.
DAG definitions are versioned in `dags/`: nightly backup at 03:00, monthly restore test on day 1 at 05:00, weekly bounded Docker cleanup on Sunday at 06:00 (America/Fortaleza). Each reports success/failure to local Healthchecks. Notification destinations remain an operator setting; no outbound messages are configured automatically.
Phase 3 requires Phase 1. Command: `cd ansible && ../.venv/bin/ansible-playbook site.yml --tags fase3 -K`.
For iterative deployment and checks with one authentication, use `.venv/bin/python scripts/deploy-session.py`. The password is passed via an anonymous file descriptor that is closed on exit; it is never persisted or printed. After deployment, use `smoke`, `backup`, `restore`, and `deploy` for the second idempotence run, then `exit`.
Ubuntu 26.04 uses sudo-rs. The inventory selects the installed traditional `/usr/bin/sudo.ws` for Ansible's custom prompt; it does not change the system default sudo.
Syntax validation does not replace deployment and integration checks.

## Deployment validation (2026-10-09)
Phase 1 and Phase 3 are deployed on Ubuntu 26.04.1 amd64 / Btrfs. Verified: nine HTTPS routes with Caddy's CA, private Git clone/push from the Mac over SSH with host-key verification, a successful Forgejo Actions job, snapshot/restic backup to MinIO, isolated restore with Git fsck and PocketBase SQLite integrity checks, valid Dagu specs, and successful backup/restore/prune pings in Healthchecks.
Observed service memory after maintenance: approximately 730 MiB total (about 617 MiB in nine containers plus 115 MiB for host Dagu). This is a spot measurement, not a workload capacity guarantee.
Run integration checks explicitly: `cd ansible && ../.venv/bin/ansible-playbook acceptance.yml -K`. This performs bounded Docker cleanup (older than seven days), checks all three monitoring pings, and reports repository/resource status. Use `smoke.yml` for Git/CI and `restore.yml` for a new isolated restore.
The MinIO image is compiled from the pinned official release source. Its built-in version string is `DEVELOPMENT.GOGET`; the release pin is recorded in the Dockerfile/build arguments and image tag.
On this Mac, DNS/hosts and browser trust for the CA are still client configuration steps. No macOS trust store changes are made automatically. Off-host MinIO replication remains pending.
