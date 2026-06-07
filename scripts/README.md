# scripts/

Helper scripts, grouped by purpose. Run them from anywhere — each `cd`s to the repo root first.

## deploy/  — production
| Script | What it does |
|--------|--------------|
| `deploy.sh` | Validates `.env`, builds & starts the prod stack (`docker-compose.prod.yml`). Main deploy entry point. |
| `ec2-setup.sh.legacy` | Old AWS EC2 provisioning (hardcoded `stock-satta.online`). Kept for reference only — **superseded by [`../../DEPLOY.md`](../../DEPLOY.md)**. |

## dev/  — local development
| Script | What it does |
|--------|--------------|
| `setup.sh` | First-time local setup: creates `.env`, starts dev `docker-compose.yml`. |
| `start.sh` | Build & start the local dev stack (frontend :3000, backend :8000). |
| `install_deps.sh` | Install backend Python deps into your virtualenv. |

## debug/  — diagnostics & checks
| Script | What it does |
|--------|--------------|
| `debug_db.sh` | Diagnose Postgres/backend connectivity inside Docker. |
| `test_setup.py` | Sanity-check the local setup. |
| `check_dependencies.py` | Verify Python dependencies. |
| `security_check.py` | One-off security audit. |
| `security_monitor.py` | Ongoing security monitoring. |

➡️ **To deploy to a new host, follow [`../DEPLOY.md`](../DEPLOY.md).**
