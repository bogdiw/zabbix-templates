# Eaton 93PM by SNMP

Zabbix 7.2 template for Eaton 93PM-G2 (and other XUPS-MIB-compatible) UPS units via SNMPv2c.

## Source
OIDs taken directly from the validated Telegraf XUPS-MIB collection in
`logmon-k8s/telegraf-hvac/values.yaml` (RO-PLO-S01 ups-a-pl / ups-b-pl @ 10.1.109.51-52).

## Contents
- ~25 scalar items: ident, battery, input, output, bypass, environment, alarms, test, config, topology
- 4 LLD discovery rules: input phases, output phases, bypass phases, environment contact sensors
- 4 value maps: ABM status, input source, output source, battery test result
- 7 triggers: low runtime, low battery capacity (warn + crit), on-battery, high load, output not normal, ambient temp high, active alarms, battery test failed

## Usage
1. Import the YAML.
2. Create host (e.g. `RO-PLO-S01-UPS-A-PL`), set SNMPv2 interface on `10.1.109.51`.
3. Apply this template + `Template Module ICMP Ping`.
4. Macro `{$SNMP_COMMUNITY}` defaults to `public`.

## Generation
Regenerate from `gen-eaton.py` if OID list changes.
