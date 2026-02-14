# Homelab Infrastructure

This repository showcases a modular, Docker-based infrastructure environment
running on a live Ubuntu Server hosted on Hetzner.

It is a sanitised version of my production homelab stack, with sensitive
information removed.

---

## 🌐 High-Level Architecture

Traffic Flow:

Internet  
→ Cloudflare DNS  
→ Hetzner Ubuntu Server  
→ Traefik Reverse Proxy (Let's Encrypt SSL)  
→ Docker Containers  

Public-facing services are attached to
