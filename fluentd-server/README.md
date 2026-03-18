# Fluentd Server

Monitors a Fluentd log aggregation server via the built-in `monitor_agent` HTTP endpoint and a custom log path freshness script.

## Components

### Service & Metrics (HTTP polling)
- Master HTTP item polls `/api/plugins.json` on port 9880
- Dependent items extract per-plugin metrics via JSONPath:
  - Buffer queue length, available space %, retry count, emit records
  - Covers all input and output plugins

### Log Path Freshness (Zabbix agent LLD)
- Custom script `/usr/local/bin/zabbix_fluentd_logcheck.py` scans the NFS logging path
- Returns JSON with each active log path and age in minutes
- LLD discovers paths, dependent items track age per path
- Triggers fire when a path goes stale (configurable via macros)

## Requirements
- Fluentd with `monitor_agent` enabled on port 9880
- Zabbix agent 2 on the Fluentd host
- Script deployed via the `fluentd-server` Ansible role

## Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$FLUENTD_HTTP_PORT}` | `9880` | monitor_agent HTTP port |
| `{$FLUENTD_FWD_PORT}` | `24224` | Fluentd forward protocol port |
| `{$LOG_AGE_WARN}` | `120` | Warning: no logs for this many minutes (2h) |
| `{$LOG_AGE_HIGH}` | `240` | High: no logs for this many minutes (4h) |

## Triggers

| Trigger | Severity |
|---------|----------|
| Host unreachable | Disaster |
| Monitor agent port 9880 down | High |
| Forward port 24224 down | High |
| Monitor agent no data (3m) | High |
| Output buffer space < 20% (client logs / firewall syslog) | High |
| Output buffer space < 20% (other plugins) | Average |
| Any output retry count > 0 | Average |
| Log path stale > `{$LOG_AGE_WARN}` min | Warning |
| Log path stale > `{$LOG_AGE_HIGH}` min | High |
