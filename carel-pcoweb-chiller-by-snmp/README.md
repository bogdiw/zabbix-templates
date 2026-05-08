# Carel pCOWeb chiller by SNMP

Zabbix 7.2 template for chillers using a Carel pCO controller with pCOWeb SNMP add-on.
Validated against Flakt GLFC0452BD2 chillers @ Brazi, but works for any pCOWeb-fronted
unit since the OID tree is the same.

## Why custom and not the community `template_airco_pcoweb`
The community `Airco pCOWeb` template assumes specific Carel index → physical-point
mappings (e.g. `ai_001` = Room Temperature) that hold for ONE OEM. Flakt uses different
indexes — every queried OID returned 0 with the community template. This template avoids
the assumption: it walks the entire tree and creates one item per *populated* index.

## Pattern
Master walk + dependent LLD per Carel kind:
- `1.3.6.1.4.1.9839.2.1.2` — analog inputs (`ai_*`), values divided by 10 (Carel convention
  for °C/bar)
- `1.3.6.1.4.1.9839.2.1.3` — integer inputs (`ii_*`), raw
- `1.3.6.1.4.1.9839.2.1.1` — digital inputs (`di_*`), 0/1

Filter drops indexes whose value is 0 (unconfigured) or `-888` (Carel sentinel for
unused analog).

## Triggers (sensor-fault detection only)
Without the OEM commissioning sheet we can't add semantic triggers (no idea which `ai_*`
is "chilled water inlet" vs "compressor capacity %"). The template ships with safety-net
trigger prototypes that fire only on physical impossibilities or sensor faults:
- `ai_*` reads >1000 → likely sensor failure / open circuit
- `ai_*` reads <-500 → likely sensor disconnect
- `ai_*` stops reporting for 10 min → controller fault
- `ai_*` jumps >100 between consecutive polls → sensor glitch
- `di_*` state change → investigate (could be alarm or compressor start)
- SNMP unreachable
- Controller restarted (uptime <10 min)

Once Flakt provides the index → physical-point map, rename specific items and add proper
operational thresholds (CHW supply >X°C, refrigerant high pressure, common alarm bit).

## Walk timeout note
The Carel pCOWeb is slow to walk the full ~5000-entry analog tree. The template sets a
60-second per-item timeout to avoid `partial data received` errors. The default Zabbix 3-second
timeout is too short.

## Usage
1. Import the YAML.
2. Create one host per chiller, SNMPv2 interface on the chiller IP.
3. Apply this template + ICMP Ping.

## Generation
Regenerate from `gen-carel.py`.
