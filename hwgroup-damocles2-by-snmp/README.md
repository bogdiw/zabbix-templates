# HW Group Damocles2 by SNMP (STUB)

Placeholder template for HW Group Damocles2 (Mini and full) sensor / fire-detection panel.

## Blocking item
Damocles2 ships with **SNMP disabled by default**. Site team must enable it on the
device first (Web UI -> System -> SNMP), then we generate items from the DAMOCLES-MIB.

## Generation procedure (once SNMP is enabled)
```bash
mib2zabbix -o 1.3.6.1.4.1.21796.4 -n "HW Group Damocles2 by SNMP" > items.yaml
```
Merge into the template skeleton in this directory.

## Inventory
- `.204` `RO-PLO-S01-CentralaDetectie01-PL` (Damocles2 Mini)
- `.207` reachable but not in the Excel inventory yet — name TBD

## Until SNMP is enabled
Use `Template Module ICMP Ping` for availability only.
