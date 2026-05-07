# Janitza UMG96RM-E by Modbus

Zabbix 7.2 template for Janitza UMG96RM-E power meters via Modbus TCP using the Zabbix
Agent 2 modbus plugin.

## Why Modbus and not SNMP
Janitza's SNMP MIB is non-standard (vendor admission) and known to be buggy. Modbus TCP
is the manufacturer-recommended path. Register map per manual `1.040.129`, live-validated
against bm-ups-a @ 10.1.109.55 (2026-05-06).

## Contents
- 61 holding-register items (FLOAT32 ABCD, big-endian, function 3, base addr 19000):
  V/I per phase + total, P/S/Q per phase + total, cosphi, frequency, rotation field,
  full energy block (active bidirectional/import/export, apparent, reactive ind/cap), THD V/I
- 4 triggers: frequency low/high, L1-N voltage low, no-data

## Prerequisite
Zabbix Agent 2 with `Plugins.Modbus.Sessions.*` configured, reachable from the Zabbix server.
The agent runs the actual modbus polls — the Zabbix server only requests via the agent.

## Usage
1. Import the YAML.
2. Create host (e.g. `RO-PLO-S01-BM-UPS-A`).
3. Apply this template + `Template Module ICMP Ping`.
4. Override macros per host:
   - `{$MODBUS.HOST}` = `tcp://10.1.109.55:502` (per meter IP)
   - `{$MODBUS.SLAVE}` = `1` (default for Janitza)

## Generation
Regenerate from `gen-janitza.py` if register list changes (e.g. when RCM CT channels are wired).
