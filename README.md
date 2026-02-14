# Homelab Infrastructure

This repository showcases a modular, Docker-based infrastructure environment
running on a live Ubuntu Server hosted on Hetzner.

It is a sanitised version of my production homelab stack, with all sensitive
information, domains, IP addresses, and secrets removed.

The goal of this repository is to demonstrate infrastructure design,
network segmentation, reverse proxy configuration, monitoring integration,
and operational practices in a real-world deployment scenario.

---

## 🌐 Architecture Overview

### Traffic Flow

Internet  
→ Cloudflare (DNS management)  
→ Hetzner Dedicated Ubuntu Server  
→ Traefik Reverse Proxy (Let's Encrypt SSL termination)  
→ Docker Container Stacks  

---

## 🔐 Network & Security Design

- Public-facing services are attached to a dedicated Traefik network.
- Internal services remain isolated on default Docker stack networks.
- Host-level access restricted via UFW firewall rules.
- Only required ports are exposed.
- SSL certificates managed automatically via Let's Encrypt.
- Secrets managed via `.env` files (not included in this repository).

This approach ensures service segmentation and minimises attack surface.

---

## 🐳 Stack Structure

Infrastructure is modular and separated by concern under `/docker/stacks/`.

Each stack contains:
- `docker-compose.yml`
- Stack-specific configuration
- Environment variable references (redacted)

### Stack Categories Include:

- Reverse Proxy (Traefik)
- Authentication (Authentik)
- Media Services
- Monitoring & Observability (Prometheus, Loki, Promtail)
- Backup Automation (Autorestic)
- Application Services (Nextcloud, Paperless, etc.)
- Game Servers
- Utility & Dashboard Services

Modularisation allows independent lifecycle management per stack.

---

## 📊 Observability

Integrated monitoring stack includes:

- Prometheus (metrics collection)
- Loki (log aggregation)
- Promtail / Fluent-bit (log forwarding)

This enables:

- Container-level log visibility
- System troubleshooting
- Service reliability tracking
- Operational debugging

---

## 💾 Backup Strategy

Backups are handled via Autorestic.

- Persistent volumes defined per service
- Scheduled backup execution
- Off-host redundancy (sanitised details)

Backup validation is part of operational maintenance.

---

## 🧠 Operational Practices

- Regular patching and container updates
- Log-based debugging using `journalctl` and container logs
- Modular stack orchestration (`up-all.sh`, `down-all.sh`)
- Post-change validation checklist
- Separation of public and internal services

This environment is actively maintained and used as a live production-style deployment.

---

## ⚠️ Important

This repository is intended as a structural and architectural showcase.

It is **not directly deployable** without:

- Creating your own `.env` files
- Replacing placeholder domains
- Supplying your own secrets
- Reviewing exposed services

---

## 👤 About Me

I am transitioning into a Junior Systems / Infrastructure / Cloud Support role and operate this environment as a practical platform for infrastructure engineering and continuous learning.

This stack reflects hands-on experience with:

- Linux server administration
- Docker-based service architecture
- Reverse proxy and SSL management
- Network segmentation
- Monitoring and logging systems
- Multi-provider infrastructure design