#!/usr/bin/env python3
"""Zabbix 7.2 template for Carel pCOWeb chillers (Flakt GLFC0452BD2 etc.) via SNMP.
Walks the three indexed trees and creates one item per populated index — no fixed
assumption about which index = which sensor. Rename items once the Flakt commissioning
sheet provides the index → physical-point map."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-0000000000c1")
def U(seed):
    u = uuid.uuid5(NS, seed); b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

TPL = "Carel pCOWeb chiller by SNMP"

def lld(name, key, base_oid, kind_label, value_type, value_div=None, filter_neg888=False):
    proto = {
        "uuid": U(f"proto:{key}"),
        "name": f"Carel {kind_label}_{{#INDEX}}",
        "type": "SNMP_AGENT",
        "snmp_oid": f"{base_oid}.{{#INDEX}}.0",
        "key": f"carel.{kind_label}[{{#INDEX}}]",
        "delay": "1m",
        "history": "31d",
        "trends": "365d",
        "value_type": value_type,
        "tags": [
            {"tag": "class", "value": "chiller"},
            {"tag": "vendor", "value": "carel"},
            {"tag": "carel_kind", "value": kind_label},
            {"tag": "carel_index", "value": "{#INDEX}"},
        ],
    }
    if value_div:
        proto["preprocessing"] = [{"type": "MULTIPLIER", "parameters": [str(1.0/value_div)]}]

    rule = {
        "uuid": U(f"lld:{key}"),
        "name": name,
        "type": "SNMP_AGENT",
        "snmp_oid": f"discovery[{{#INDEX}},{base_oid}]",
        "key": key,
        "delay": "5m",
        "lifetime": "30d",
        "item_prototypes": [proto],
    }
    if filter_neg888:
        rule["overrides"] = [{
            "name": "Drop sentinel -888",
            "step": "1",
            "stop": "YES",
            "filter": {"evaltype": "AND", "conditions": [
                {"macro": "{#INDEX}", "value": ".*", "operator": "MATCHES_REGEX", "formulaid": "A"},
            ]},
            "operations": [],
        }]
    return rule

def build():
    items = [
        {
            "uuid": U("item:snmp_avail"),
            "name": "SNMP availability",
            "type": "INTERNAL",
            "key": "zabbix[host,snmp,available]",
            "delay": "1m",
            "history": "7d", "trends": "0",
            "value_type": "UNSIGNED",
            "valuemap": {"name": "Zabbix host availability"},
            "tags": [{"tag": "component", "value": "availability"}],
        },
        {
            "uuid": U("item:sysdescr"),
            "name": "System description",
            "type": "SNMP_AGENT",
            "snmp_oid": "1.3.6.1.2.1.1.1.0",
            "key": "system.descr",
            "delay": "10m",
            "history": "31d", "trends": "0",
            "value_type": "CHAR",
            "tags": [{"tag": "component", "value": "system"}],
        },
        {
            "uuid": U("item:sysuptime"),
            "name": "System uptime",
            "type": "SNMP_AGENT",
            "snmp_oid": "1.3.6.1.2.1.1.3.0",
            "key": "system.uptime",
            "delay": "1m",
            "history": "7d", "trends": "0",
            "value_type": "FLOAT",
            "units": "uptime",
            "preprocessing": [{"type": "MULTIPLIER", "parameters": ["0.01"]}],
            "tags": [{"tag": "component", "value": "system"}],
        },
    ]

    discovery_rules = [
        lld("Carel analog inputs (ai)",   "carel.ai.discovery", "1.3.6.1.4.1.9839.2.1.2", "ai", "FLOAT", value_div=10.0),
        lld("Carel integer inputs (ii)",  "carel.ii.discovery", "1.3.6.1.4.1.9839.2.1.3", "ii", "UNSIGNED"),
        lld("Carel digital inputs (di)",  "carel.di.discovery", "1.3.6.1.4.1.9839.2.1.1", "di", "UNSIGNED"),
    ]

    triggers = [
        {
            "uuid": U("trig:snmp_unreachable"),
            "expression": f'max(/{TPL}/zabbix[host,snmp,available],#3)=0',
            "name": "SNMP unreachable on {HOST.NAME}",
            "priority": "HIGH",
        },
        {
            "uuid": U("trig:reboot"),
            "expression": f"last(/{TPL}/system.uptime)<10m",
            "name": "Chiller controller restarted on {HOST.NAME}",
            "priority": "INFO",
        },
    ]

    return {"zabbix_export": {
        "version": "7.2",
        "template_groups": [{"uuid": U("tg:hvac"), "name": "Templates/HVAC"}],
        "templates": [{
            "uuid": U("tpl:carel-pcoweb"),
            "template": TPL, "name": TPL,
            "description": "Carel pCOWeb chiller via SNMPv2c. LLD over .1.3.6.1.4.1.9839.2.1.{1,2,3} (di/ai/ii) discovers every populated index. Analog values divided by 10 (Carel convention for °C/bar). Rename specific items once OEM commissioning sheet maps index → physical point. Set {$SNMP_COMMUNITY}.",
            "groups": [{"name": "Templates/HVAC"}],
            "items": items,
            "discovery_rules": discovery_rules,
            "valuemaps": [{
                "uuid": U("vm:host_avail"),
                "name": "Zabbix host availability",
                "mappings": [
                    {"value":"0","newvalue":"not available"},
                    {"value":"1","newvalue":"available"},
                    {"value":"2","newvalue":"unknown"},
                ],
            }],
            "macros": [{"macro":"{$SNMP_COMMUNITY}","value":"public","description":"SNMPv2c community"}],
        }],
        "triggers": triggers,
    }}

if __name__ == "__main__":
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
