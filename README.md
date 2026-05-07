# Zabbix Templates Collection

A collection of custom Zabbix monitoring templates for Liberty Global Platform Infrastructure.

## Templates

| Template | Type | Description |
|----------|------|-------------|
| [Fluentd Server](fluentd-server/) | HTTP + Agent | Fluentd log server monitoring via monitor_agent HTTP API + log path freshness script |
| [NFS Mount Monitoring](nfs-mount-monitoring/) | Agent (LLD) | Generic NFS mount monitoring with configurable path filter and thresholds |
| [PowerDNS Authoritative](powerdns-authoritative/) | HTTP | PowerDNS Authoritative Server via built-in HTTP API |
| [PowerDNS Recursor](powerdns-recursor/) | Agent | PowerDNS Recursor via `rec_control` UserParameter |
| [Grafana by HTTP](grafana-by-http/) | HTTP | Grafana health monitoring via `/api/health` endpoint |
| [Storware Backup and Recovery](storware/) | REST API | Storware vProtect/Backup & Recovery monitoring |
| [Proxmox DDBoost Backup](proxmox-ddboost-backup/) | Agent | Proxmox VM backup status on DDBoost storage |

| [Grafana Alerts Aggregator](grafana-by-http/) | HTTP | Pulls Grafana alert states into Zabbix via Prometheus-compatible API (LLD per alert rule) |

## Other

| Item | Description |
|------|-------------|
| [Emergency Dashboard](emergency-dashboard/) | Zabbix dashboard backup — Platform & Infrastructure overview |
| [BGP WAN Routers Validation](bgp-wan-routers-validation.md) | Audit and setup documentation for WAN router BGP monitoring |
