# Grafana by HTTP

Monitors Grafana via the `/api/health` HTTP endpoint.

## Requirements
- Network access from Zabbix server to Grafana HTTP port
- Grafana API credentials (optional, for authenticated endpoints)

## Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$GRAFANA.HOST}` | `<SET>` | Grafana hostname/IP |
| `{$GRAFANA.PORT}` | `3000` | Grafana HTTP port |
| `{$GRAFANA.SCHEME}` | `https` | http or https |
| `{$GRAFANA.USER}` | `` | API user (optional) |
| `{$GRAFANA.PASSWORD}` | `` | API password (optional) |
| `{$GRAFANA.RESPONSE_TIME.MAX.WARN}` | `5` | Max response time (seconds) |

## Items (6)
- Get health (master HTTP item)
- Database status, Version (dependent)
- Service status (1=healthy, 0=unhealthy)
- Service availability (port check)
- Service response time

## Triggers
- Service down — High
- Database unhealthy — High
- High response time (>5s for 5m) — Warning
- Version changed — Info
- No data for 5 minutes — Average
