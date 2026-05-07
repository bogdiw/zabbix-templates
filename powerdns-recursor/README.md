# PowerDNS Recursor by Zabbix agent

Monitors a PowerDNS Recursor via `rec_control get` UserParameter.

## Requirements
- Zabbix agent 2 on the recursor host
- `rec_control` accessible via sudo for the zabbix user

## Setup

Deploy UserParameter config:
```
# /etc/zabbix/zabbix_agent2.d/pdns_recursor.conf
UserParameter=pdns.recursor.stats,sudo /usr/bin/rec_control get-all
UserParameter=pdns.rec.get[*],sudo /usr/bin/rec_control get $1
```

Deploy sudoers:
```
# /etc/sudoers.d/zabbix-pdns
zabbix ALL=(root) NOPASSWD: /usr/bin/rec_control
```

## Items (15)
- Questions, outgoing queries (rate)
- Cache hits/misses (rate), cache entries
- Concurrent queries
- Servfail, NXDOMAIN, NOERROR answers (rate)
- Answer latency buckets (0-1ms, 1-10ms, 10-100ms, 100-1000ms, >1s)
- Uptime

## Triggers
- Service down (no data 5m) — High
- Restarted (uptime < 10m) — Info
- High servfail rate — Average
- Slow answers detected — Warning
