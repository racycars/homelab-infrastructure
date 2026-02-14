# Homelab Infrastructure

This repository showcases a modular, Docker-based infrastructure environment
running on a live Ubuntu Server hosted on Hetzner.

It is a sanitised version of my production homelab stack, with all sensitive
information, domains, IP addresses, and secrets removed.

---

## 🌐 High-Level Architecture

Traffic Flow:

Internet  
→ Cloudflare DNS  
→ Hetzner Ubuntu Server  
→ Traefik Reverse Proxy (Let's Encrypt SSL)  
→ Docker Containers  

### Network Segmentation

- Public-facing services are attached to a dedicated Traefik network.
- Internal services remain isolated on default Docker networks.
- Host-level access is restricted via UFW firewall rules.
- Only required ports are exposed.

---

## 🐳 Stack Structure

The infrastructure is split into modular stacks located in `/stacks/`.

Each stack contains:

- `docker-compose.yml`
- Stack-specific configuration
- Environment variable references (redacted)

### Example Stack Categories

- Reverse Proxy (Traefik)
- Authentication (Authentik)
- Media Services
- Monitoring & Observability (Prometheus, Loki, Promtail)
- Backup (Autorestic)
- Cloud Storage / File Services
- Application Services (Nextcloud, Paperless, etc.)

---

## 🔐 Security Approach

- UFW firewall used to restrict host-level exposure.
- Traefik handles SSL termination via Let's Encrypt.
- Secrets managed via `.env` files (not included in this repo).
- Services segmented by Docker network boundaries.
- Public services isolated from internal-only services.

---

## 📊 Observability

Integrated monitoring stack includes:

- Prometheus (metrics)
- Loki (log aggregation)
- Promtail / Fluent-bit (log shipping)

This allows:

- Container-level log monitoring
- System troubleshooting
- Service reliability tracking

---

## 💾 Backup Strategy

Backups managed via Autorestic with scheduled execution.

- Service data stored on persistent volumes
- Backup policies configured per stack
- Off-host redundancy (sanitised details)

---

## 🧠 Operational Practices

- Regular patching and container updates
- Log-based debugging (`journalctl`, container logs)
- Modular stack management (`up-all.sh`, `down-all.sh`)
- Post-change validation checklist

---

## 🚀 Goals of This Environment

- Maintain a production-style Linux server environment
- Practice infrastructure security and network segmentation
- Operate containerised services at scale
- Implement monitoring and logging best practices
- Simulate real-world multi-provider architecture

---

## ⚠️ Important

This repository is intended as a structural showcase only.

It is not directly deployable without:

- Creating your own `.env` files
- Replacing placeholder domains
- Configuring your own secrets
- Reviewing exposed services

---

## 👤 About Me

I am transitioning into a Junior Systems / Infrastructure / Cloud Support role and
operate this environment as a practical learning and operational platform.
