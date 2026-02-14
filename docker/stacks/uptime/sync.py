import os
import re
import time
from pathlib import Path
import yaml
from uptime_kuma_api import UptimeKumaApi

# Matches: Host(`example.com`) or Host(`example.com`,`example.com`)
HOST_BLOCK_RE = re.compile(r"Host\(([^)]+)\)")
BACKTICK_RE = re.compile(r"`([^`]+)`")

# Matches: traefik.http.services.<svc>.loadbalancer.server.port
LB_PORT_RE = re.compile(r"^traefik\.http\.services\.[^.]+\.loadbalancer\.server\.port$")

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

def labels_to_dict(labels):
    """Compose labels can be list of 'k=v' or dict {k:v}."""
    if labels is None:
        return {}
    if isinstance(labels, dict):
        return {str(k): str(v) for k, v in labels.items()}
    if isinstance(labels, list):
        out = {}
        for item in labels:
            if isinstance(item, str) and "=" in item:
                k, v = item.split("=", 1)
                out[k.strip()] = v.strip()
        return out
    return {}

def expand_domain(value: str, domain: str) -> str:
    if not isinstance(value, str):
        return ""
    if not domain:
        return value
    return value.replace("${DOMAIN}", domain).replace("$DOMAIN", domain)

def safe_load_yaml(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARN] YAML parse failed: {path} ({e})")
        return None

def find_yaml_files(root: Path):
    files = set()
    for pat in ("**/*.yml", "**/*.yaml"):
        for p in root.glob(pat):
            if p.is_file():
                files.add(p.resolve())
    return sorted(files)

def resolve_includes(meta_file: Path):
    """Supports:
      include:
        - stacks/media/docker-compose.yml
        - stacks/traefik/docker-compose.yml
    """
    data = safe_load_yaml(meta_file)
    if not isinstance(data, dict):
        return []

    inc = data.get("include")
    if not inc:
        return []

    if not isinstance(inc, list):
        print(f"[WARN] include in {meta_file} is not a list; ignoring")
        return []

    resolved = []
    for item in inc:
        if not isinstance(item, str):
            continue
        p = (meta_file.parent / item).resolve()
        if p.exists() and p.is_file():
            resolved.append(p)
        else:
            print(f"[WARN] include target missing: {p}")
    return resolved

def extract_public_urls_from_rule(rule: str, domain: str):
    """Extract hosts from Traefik rule strings and return https URLs."""
    if not isinstance(rule, str):
        return []
    urls = []
    for host_block in HOST_BLOCK_RE.findall(rule):
        for host in BACKTICK_RE.findall(host_block):
            host = expand_domain(host, domain).strip()
            if host:
                urls.append(f"https://{host}")
    return urls

def extract_backend_port(labels: dict):
    """Pick a backend port from traefik.http.services.*.loadbalancer.server.port."""
    for k, v in labels.items():
        if LB_PORT_RE.match(k):
            try:
                return int(str(v).strip())
            except Exception:
                continue
    return None

def choose_backend_host(service_dict: dict, service_name: str) -> str:
    """
    Prefer container_name if present; otherwise service name.
    On Docker networks, both commonly resolve; service name is always safe in Compose networks.
    """
    cn = service_dict.get("container_name")
    if isinstance(cn, str) and cn.strip():
        return cn.strip()
    return service_name

def discover_targets(compose_root: Path, domain: str, only_included: bool):
    """
    Returns:
      public_targets: dict monitor_name -> url
      backend_targets: dict monitor_name -> url
    """
    all_files = find_yaml_files(compose_root)

    included_files = []
    for f in all_files:
        data = safe_load_yaml(f)
        if isinstance(data, dict) and "include" in data:
            included_files.extend(resolve_includes(f))

    if only_included and included_files:
        scan_files = sorted(set(included_files))
    else:
        scan_files = sorted(set(all_files) | set(included_files))

    public_targets = {}
    backend_targets = {}

    for path in scan_files:
        data = safe_load_yaml(path)

        # Skip YAML that isn't a compose dict
        if not isinstance(data, dict):
            continue

        services = data.get("services")
        if not isinstance(services, dict):
            continue

        for svc_name, svc in services.items():
            if not isinstance(svc, dict):
                continue

            labels = labels_to_dict(svc.get("labels"))

            # We only build targets from things that are exposed via Traefik OR have homepage.href
            traefik_enabled = labels.get("traefik.enable", "false").lower() in ("true", "1", "yes", "on")
            homepage_href = labels.get("homepage.href")
            display_name = labels.get("homepage.name", svc_name)

            # ---------- PUBLIC TARGET ----------
            public_urls = []
            if isinstance(homepage_href, str) and homepage_href.strip():
                public_urls = [expand_domain(homepage_href.strip(), domain)]
            elif traefik_enabled:
                rule_keys = [k for k in labels.keys() if k.endswith(".rule")]
                for k in sorted(rule_keys):
                    urls = extract_public_urls_from_rule(labels.get(k, ""), domain)
                    if urls:
                        public_urls = urls
                        break

            # Save public monitors
            if public_urls:
                if len(public_urls) == 1:
                    public_targets[f"{display_name} (public)"] = public_urls[0]
                else:
                    for u in public_urls:
                        host = u.replace("https://", "")
                        public_targets[f"{display_name} (public) ({host})"] = u

            # ---------- BACKEND TARGET ----------
            # Only if Traefik is enabled AND we can find the internal port label
            if traefik_enabled:
                port = extract_backend_port(labels)
                if port:
                    backend_host = choose_backend_host(svc, svc_name)
                    backend_url = f"http://{backend_host}:{port}"
                    backend_targets[f"{display_name} (backend)"] = backend_url

    return public_targets, backend_targets

def main():
    kuma_url = os.getenv("KUMA_URL", "http://uptime-kuma:3001").rstrip("/")
    kuma_user = os.getenv("KUMA_USERNAME")
    kuma_pass = os.getenv("KUMA_PASSWORD")
    domain = os.getenv("DOMAIN", "")
    compose_dir = os.getenv("COMPOSE_DIR", "/compose")
    interval = int(os.getenv("SYNC_INTERVAL", "600"))

    # Optional behaviors
    update_existing = env_bool("UPDATE_EXISTING", False)
    only_included = env_bool("ONLY_INCLUDED", False)

    if not kuma_user or not kuma_pass:
        raise SystemExit("[FATAL] KUMA_USERNAME / KUMA_PASSWORD not set")

    compose_root = Path(compose_dir)
    if not compose_root.exists():
        raise SystemExit(f"[FATAL] COMPOSE_DIR does not exist: {compose_root}")

    api = UptimeKumaApi(kuma_url)
    api.login(kuma_user, kuma_pass)

    print(f"[INFO] Connected to Uptime Kuma at {kuma_url}")
    print(f"[INFO] Scanning compose under: {compose_root}")
    if domain:
        print(f"[INFO] DOMAIN expansion: {domain}")
    if update_existing:
        print("[INFO] UPDATE_EXISTING=true (will update URLs if changed)")
    if only_included:
        print("[INFO] ONLY_INCLUDED=true (scan only include: targets if present)")

    while True:
        try:
            public_targets, backend_targets = discover_targets(compose_root, domain, only_included)
            all_targets = {}
            all_targets.update(public_targets)
            all_targets.update(backend_targets)

            print(f"[INFO] Discovered public={len(public_targets)} backend={len(backend_targets)} total={len(all_targets)}")

            monitors = api.get_monitors()
            existing_by_name = {m["name"]: m for m in monitors}

            created = 0
            updated = 0

            for name, url in sorted(all_targets.items()):
                if name not in existing_by_name:
                    try:
                        # NOTE: accepted_statuscodes intentionally NOT set (avoids API rejection)
                        api.add_monitor(
                            type="http",
                            name=name,
                            url=url,
                            interval=60,
                            retryInterval=60,
                            maxretries=2,
                            timeout=10,
                        )
                        print(f"[ADD] {name} -> {url}")
                        created += 1
                    except Exception as e:
                        print(f"[FAIL] add {name}: {e}")
                else:
                    if update_existing:
                        mon = existing_by_name[name]
                        old_url = mon.get("url")
                        if old_url and old_url != url:
                            try:
                                api.edit_monitor(mon["id"], url=url)
                                print(f"[UPD] {name}: {old_url} -> {url}")
                                updated += 1
                            except Exception as e:
                                print(f"[FAIL] update {name}: {e}")

            print(f"[DONE] created={created} updated={updated} next_sync={interval}s")

        except Exception as e:
            print(f"[ERROR] sync failed: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    main()