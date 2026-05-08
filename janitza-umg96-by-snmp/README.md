# Janitza UMG96 by SNMP

Zabbix 7.2 template for Janitza UMG96RM-E and family power meters via SNMPv2c.

## Why SNMP and not Modbus
The original plan was Modbus TCP (matching the Telegraf collector). After live-probing the
device on 2026-05-08, the Janitza SNMP MIB at enterprise OID `1.3.6.1.4.1.34278` returned
all expected fields cleanly — values matched our Modbus readings exactly. Modern firmware
makes SNMP fully usable. The Modbus path (which would have required deploying a Zabbix
Agent2 with the modbus plugin) was dropped.

## Contents
- 45 SNMP items: V/I per phase, V L-L, P/Q/S per phase + totals, cosphi per phase + total,
  energy active/reactive per phase + totals, THD voltage/current per phase, frequency,
  rotation field, device label
- 26 triggers: voltage L1/L2/L3 low/high warn/crit, frequency low/high warn/crit, THD-V
  warn/crit per phase, power factor low, energy counter reset, SNMP unreachable, no-data
- All thresholds via macros: `{$V.LOW.WARN}`, `{$V.HIGH.CRIT}`, `{$FREQ.LOW.WARN}`,
  `{$THD.V.WARN}`, `{$PF.LOW.WARN}`, etc.

## Trigger thresholds (defaults)
- Voltage: ±10% / ±15% per EN 50160 (207-253V warn, 195-264V crit)
- Frequency: 50 Hz ±1% / ±2% per EN 50160 (49.5-50.5 warn, 49-51 crit)
- THD voltage: 5% warn, 8% crit per EN 50160 / IEEE 519-2014
- Power factor: <0.7 informational

## Usage
1. Import the YAML.
2. Create one host per meter, SNMPv2 interface on the meter IP.
3. Apply this template + `Template Module ICMP Ping`.
4. Override macros per-host if some rails have different nominal voltage / tighter limits.

## Generation
Regenerate from `gen-janitza-snmp.py` if OID list or default thresholds change.
