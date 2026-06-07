# Deploying Stock AI (cheap / free hosting)

This app is a 5-container stack run by `docker-compose.prod.yml`:
**postgres · redis · backend (FastAPI) · frontend (React, built static) · nginx (SSL reverse proxy)**.

The public hostname is driven by a single env var, `DOMAIN`. Set it once in `.env`
and both nginx and the frontend build use it — no more hardcoded domains.

---

## Recommended: Oracle Cloud "Always Free" VM + DuckDNS (cost: $0/forever)

This is the closest thing to your old EC2 box, but free forever. You get a VM with
a public IP; DuckDNS gives you a free subdomain that points at that IP; Let's Encrypt
gives you HTTPS.

> ⏱️ **Heads up:** Oracle's free **ARM (Ampere A1)** shape is often "out of capacity."
> If the launch fails, retry, or switch home region. If it keeps failing and you're on
> a deadline, jump to the **Render fallback** at the bottom — same repo, ~10 min.

### 1. Create the VM
1. Sign up at <https://cloud.oracle.com> (needs a card for verification; not charged).
2. **Compute → Instances → Create instance.**
   - Image: **Canonical Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (ARM) — give it **2 OCPU / 12 GB** (well within free tier).
     - If "out of host capacity": retry, or try shape **VM.Standard.E2.1.Micro** (AMD, 1 GB — tight but works for a low-traffic demo).
   - Add your SSH public key (or let it generate one and download it).
3. **Networking → VCN → Security List:** add **Ingress rules** allowing TCP **80** and **443** from `0.0.0.0/0` (port 22 is open by default).
4. Note the instance's **public IP**.

### 2. Free subdomain via DuckDNS
1. Go to <https://www.duckdns.org>, sign in (GitHub/Google), create a subdomain, e.g. `stock-ai-demo`.
2. Set its **IP** to your Oracle VM's public IP. Your URL is now `stock-ai-demo.duckdns.org`.

### 3. SSH in and install Docker
```bash
ssh -i /path/to/key ubuntu@<PUBLIC_IP>

sudo apt update && sudo apt upgrade -y
# Docker + compose plugin
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Oracle Ubuntu blocks ports at the OS firewall too — open 80/443:
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
# log out & back in so the docker group applies
exit
```

### 4. Get the code + secrets
```bash
ssh -i /path/to/key ubuntu@<PUBLIC_IP>
git clone <your-repo-url> stock-ai && cd stock-ai

cp env.example .env
nano .env    # paste your secrets from the OLD EC2 .env, and set:
             #   DOMAIN=stock-ai-demo.duckdns.org
             #   FRONTEND_URL=https://stock-ai-demo.duckdns.org
             #   BACKEND_CORS_ORIGINS=https://stock-ai-demo.duckdns.org
```
> 💡 Grab the old secrets from EC2 with: `scp -i ec2key.pem ubuntu@<EC2_IP>:~/stock-ai/.env ./ec2.env`
> then copy the secret values across. **Do not reuse** the old `DOMAIN`/URL lines.

### 5. Issue the SSL certificate (one time)
nginx needs the cert to exist before it starts. Get it with certbot in standalone mode
(nothing is on port 80 yet):
```bash
sudo apt install -y certbot
sudo certbot certonly --standalone \
  -d stock-ai-demo.duckdns.org \
  --non-interactive --agree-tos -m you@example.com
# certs land in /etc/letsencrypt/live/... which the nginx container mounts read-only
```

### 6. Launch
```bash
./scripts/deploy/deploy.sh         # builds images + starts the stack
# or directly:
docker compose -f docker-compose.prod.yml up -d --build
```
Visit **https://stock-ai-demo.duckdns.org** 🎉

### 7. Cert auto-renewal
```bash
# renew quarterly; reload nginx container after
sudo crontab -e
# add:
0 3 1 */2 * certbot renew --quiet && docker restart stock_ai_nginx_prod
```

### Turning it off to save resources (it's free, but if you want)
```bash
docker compose -f docker-compose.prod.yml down     # stop
docker compose -f docker-compose.prod.yml up -d     # start again later
```

---

## Render (free subdomains, fastest, sleeps when idle) — via `render.yaml`

Render runs each piece free and sleeps it when idle (cold start ~50s — fine for a demo).
The repo includes **`render.yaml`** (a Blueprint) that defines all four pieces:
managed **Postgres**, **Key Value (Redis)**, the **backend** (from `backend/Dockerfile`),
and the **frontend** (static Vite build). No nginx, no SSL setup, no domain to buy.

### Steps
1. Push this repo to GitHub/GitLab (you said you'll commit — make sure `render.yaml` is in it).
2. Go to <https://dashboard.render.com> → sign up (GitHub login is easiest, **no card needed** for free tier).
3. **New ➜ Blueprint** → connect your repo → Render detects `render.yaml` and lists the 4 resources.
4. It will **prompt you for each `sync: false` secret** — paste these from your old EC2 `.env`:
   `JWT_SECRET` (≥32 chars), `FERNET_KEY` (≥44 chars), `GOOGLE_CLIENT_ID/SECRET`,
   `ZERODHA_API_KEY/SECRET`, and (optional but needed for email login) the `SMTP_*`, `FROM_*`, `OPENAI_API_KEY`.
   `DATABASE_URL` and `REDIS_URL` are wired automatically — leave them.
5. **Apply.** First build takes ~5–10 min (backend installs pandas/numpy). Watch the logs.
6. Your URLs: frontend **https://stockai-frontend.onrender.com**, backend **https://stockai-backend.onrender.com**.

### Two things to verify after first deploy
- **Service-name collision:** if Render appended a suffix (e.g. `stockai-backend-a1b2`),
  the baked-in `VITE_API_URL` / `BACKEND_CORS_ORIGINS` are now wrong. Fix them in each
  service's **Environment** tab to the real URLs and redeploy. (Rename the services to
  something unique up front to avoid this.)
- **OAuth / Zerodha callbacks:** add the new frontend URL to your Google OAuth authorized
  origins/redirects and Zerodha redirect URL, or those logins fail.

### Two known free-tier caveats (matter for a portfolio link)
- **Free Postgres is deleted after ~30 days.** For a link that must survive, create a free
  **Neon** (neon.tech) or **Supabase** Postgres instead and just set the backend's
  `DATABASE_URL` to its connection string (the code normalizes `postgres://` automatically).
- **Services sleep when idle** → first visit after a while spins for ~50s. Fine for a demo;
  mention it to anyone you share with, or add a cheap uptime pinger if it bothers you.

---

## Notes
- **Database starts empty** on the new host. For a portfolio demo just re-register.
  To migrate real data: `pg_dump` from EC2 → `psql` into the new postgres container.
- **Celery** is in `requirements.txt` but no worker runs in `docker-compose.prod.yml`
  (only uvicorn via `backend/startup.sh`). Background tasks aren't active in prod today.
- **Drop the old domain:** don't renew `stock-satta.online` at Namecheap's $44 — DuckDNS
  is free. Just update Google OAuth + Zerodha redirect/callback URLs to the new domain
  in their consoles, or those logins will fail.
