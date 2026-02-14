# Split stacks (Portainer-friendly)

You currently have a **single** `docker-compose.yml` that uses `include:` to pull in all stack compose files.
That makes Portainer (and `docker compose`) treat it as one big project.

This export renames that file to:

- `docker-compose.all.yml` (kept as a convenience if you ever want the "one big stack" view again)

## How to run as separate stacks (recommended)

### Option A — CLI (fastest)

From the `docker/` folder:

```bash
chmod +x up-all.sh down-all.sh ps-all.sh
./up-all.sh
```

Each stack is started with its own project name (e.g. `traefik`, `arrs`, `paperless`), so they show up separately in `docker ps` labels and Portainer.

To stop everything:

```bash
./down-all.sh
```

### Option B — Portainer

Create **one Portainer stack per folder** under `docker/stacks/<stackname>/`, using that folder's compose file:

- Most are `docker-compose.yml`
- Homepage uses `compose.yaml`

Tip: set the Portainer stack name to match the folder name (e.g. `arrs`, `uptime`, `traefik`) for clarity.

## Notes

- This does **not** change your service definitions; it only changes how you deploy them.
- If you rely on a shared Traefik network, ensure your stacks reference an **external** network consistently (common names: `proxy`, `traefik`).
  If you want, tell me what your Traefik network is called and I can standardize every stack for you.

### Traefik network
All stacks are now attached to a shared **external** network named `traefik`.
Create it once:
```bash
docker network create traefik
```


## Changes applied (requested)

1) **Startup order**
- `up-all.sh` now starts: `traefik` → `authentik` → `homepage` → everything else.
- `down-all.sh` stops in reverse order.

2) **Remove unused default networks / restore isolation**
- Each stack now uses its **own internal default network** (isolated per project).
- Only services that have Traefik labels are connected to the shared external `traefik` network.

3) **Lock down exposure**
- For services routed by Traefik (those with `traefik.*` labels), host **`ports:` mappings were removed** so they are not directly exposed.
- Exceptions:
  - Services using `network_mode: host` are inherently exposed (cannot be restricted by Compose networks).
  - Game servers and other non-HTTP services that are not routed by Traefik keep their ports.

If anything you still want exposed locally (without going through Traefik), tell me which service(s) and I’ll add explicit safe `ports:` back.
