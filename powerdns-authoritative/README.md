# PowerDNS Authoritative by HTTP

Monitors a PowerDNS Authoritative Server via the built-in HTTP API.

## Requirements
- PowerDNS with webserver and API enabled (`webserver=yes`, `api=yes` in `pdns.conf`)
- Network access from Zabbix server to PowerDNS API port

## Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$PDNS.API.HOST}` | `localhost` | PowerDNS API host/IP |
| `{$PDNS.API.PORT}` | `8081` | PowerDNS API port |
| `{$PDNS.API.KEY}` | `` | PowerDNS API key |

## Items (14)
- UDP/TCP queries and answers (rate)
- Backend queries (rate) and latency
- Cache hits/misses (rate) and latency
- Servfail, corrupt, timed out packets
- Uptime, security status

## Triggers
- Service down (no data 5m) — High
- Restarted (uptime < 10m) — Info
- Servfail packets detected — Warning
- Corrupt packets detected — Average
- Security status not OK — High
