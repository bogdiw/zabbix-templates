# HPE Aruba Instant On 1830 by SNMP

Zabbix 7.2 template for HPE Aruba Instant On 1830 (JL814A and family) via SNMPv2c.

Live-probed sysObjectID: `enterprises.11.2.3.7.11.210`. ifNumber=71 on the 48p model.

## Contents
- SNMPv2-MIB scalars: sysDescr, sysObjectID, uptime, contact, name, location, ifNumber
- IF-MIB LLD over `ifName` with item prototypes: oper status, admin status, in/out bits/s
  (uses 64-bit HC counters via `ifHCInOctets`/`ifHCOutOctets`)
- Trigger prototype: interface down (admin up + oper down)
- Reboot trigger on uptime < 10m

## Note
HPE Instant On line lacks public CPU/temperature MIBs (proprietary, undocumented).
This template covers what's reliably accessible via standard MIBs.

## Usage
1. Import.
2. Create host (e.g. `RO-PLO-S01-Facilities-MGMT-SW01`), SNMPv2 on `10.1.109.254`.
3. Apply template + ICMP Ping.
4. Macro `{$SNMP_COMMUNITY}` defaults to `public`.

## Generation
Regenerate from `gen-hpe.py`.
