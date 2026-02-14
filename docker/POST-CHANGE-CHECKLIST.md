# Post-change checklist

1) Create the shared Traefik network (once):
```bash
docker network create traefik
```

2) Start everything (ordered):
```bash
cd docker
./up-all.sh
```

3) Confirm routed services are NOT exposing host ports:
```bash
docker ps --format "table {{.Names}}	{{.Ports}}"
```

4) If any UI is unreachable, check:
- Traefik dashboard/logs
- Service is attached to `traefik` network
- Correct `traefik.http.routers.*.rule` hostnames

5) If a non-HTTP service needs direct access (e.g. game server), keep/restore `ports:` in its stack.
