# Wazuh Manager by HTTP

Monitors a Wazuh 4.x manager cluster from Zabbix with **no agent on the Wazuh box** — two
HTTP Script items call the Wazuh REST API and the wazuh-indexer (OpenSearch) directly.

## What it collects

**From the Wazuh manager API** (`{$WAZUH.API.URL}`, JWT auth):
- agents active / disconnected / never-connected / total
- core daemon state (analysisd, remoted)

**From the wazuh-indexer** (`{$WAZUH.INDEXER.URL}`, basic auth) — 24h rolling window over `wazuh-alerts-*`:
- alert counts per severity: Critical (rule.level ≥ 15) · High (12–14) · Medium (7–11) · Low (0–6) · total
- newest alert **text** per severity (agent + rule description), via an OpenSearch `top_hits` aggregation

## Triggers (PowerStore-style — alert text in the problem name)

| Trigger name | Zabbix severity | Fires when |
|---|---|---|
| `Wazuh Critical alert on {HOST.NAME}: {ITEM.LASTVALUE2}` | High | Critical count >0 (24h) |
| `Wazuh High alert on {HOST.NAME}: {ITEM.LASTVALUE2}` | High | High count >0 (24h) |
| `Wazuh Medium alert on {HOST.NAME}: {ITEM.LASTVALUE2}` | Average | Medium count >0 (24h) |
| `Wazuh: API unreachable or collector failing` | High | no data 10m |
| `Wazuh: ALL agents disconnected` | High | active=0 while total>0 |
| `Wazuh: more than {$WAZUH.AGENTS.DISC.MAX} agents disconnected` | Average | disconnected > macro (15m) |
| `Wazuh: core daemon not running (analysisd/remoted)` | High | either ≠ running |

The alert triggers embed the newest alert text via `{ITEM.LASTVALUE2}` (the per-severity text item is
the 2nd operand), so the Zabbix problem row and notification emails read e.g.
`Wazuh Medium alert on RO-PLO-S01 Wazuh Manager: [Medium] host-x: sshd brute force ...`.
All alert triggers have **manual close enabled** (rolling-window model — see Behavior).

Severity cap is **High** by design (no Disaster). Wazuh Critical & High → Zabbix High; Medium → Average.

## Behavior — how alerts "clear"

Wazuh alerts are **immutable log events**, not stateful alarms. These triggers are a rolling
`now-24h` count: a severity trigger stays in PROBLEM while ≥1 alert of that level exists in the last
24h, and **auto-resolves when they age out**. Manual close is allowed for dismissing transient ones;
genuinely new activity re-opens a fresh problem. Tune the window in the master item's query
(`now-24h`) if a shorter horizon is wanted.

## Macros

| Macro | Purpose |
|---|---|
| `{$WAZUH.API.URL}` | Wazuh manager API base (e.g. `https://wazuh-api.infra.cloudxedge.com`) |
| `{$WAZUH.API.USER}` / `{$WAZUH.API.PASSWORD}` | API user (secret). CloudxEdge: k8s secret `wazuh-api-cred` in ns `wazuh` (user `wazuh-wui`) |
| `{$WAZUH.INDEXER.URL}` | wazuh-indexer URL. In-cluster works when Zabbix server runs on the same cluster: `https://indexer.wazuh.svc.cluster.local:9200` |
| `{$WAZUH.INDEXER.USER}` / `{$WAZUH.INDEXER.PASSWORD}` | indexer creds (secret). CloudxEdge: k8s secret `indexer-cred` (user `admin`) |
| `{$WAZUH.AGENTS.DISC.MAX}` | tolerated disconnected agents before Average trigger (default 5) |

## Setup

1. Import `wazuh-manager-by-http.yaml` (Data collection → Templates → Import).
2. Create a host (e.g. `RO-PLO-S01 Wazuh Manager`), link the template.
3. Set the 5 macros on the host. **Secret macros (type Secret) MUST be set via API with
   `usermacro.create`, NOT `host.update` with a macro list** — a full macro-list update wipes secret
   values (they don't round-trip through `*.get`).
4. Force a poll on the master items (task.create type 6) to validate; items should populate in ~1 poll.

## CloudxEdge notes (RO-PLO-S01)

- Wazuh runs on `logmon-k8s` (ns `wazuh`): manager master/worker, indexer, dashboard. API ingress
  `wazuh-api.infra.cloudxedge.com`, dashboard `wazuh.infra.cloudxedge.com`.
- The Zabbix server runs on the same logmon cluster → the indexer Script item uses the in-cluster
  Service DNS (`indexer.wazuh.svc.cluster.local:9200`), no ingress exposure needed.
- Verified end-to-end 2026-07-17: injected synthetic sshd brute-force events → indexer → Medium
  trigger fired with the alert text as the problem name; test docs (`location:zabbix-e2e-test`) then
  deleted via `_delete_by_query`.
