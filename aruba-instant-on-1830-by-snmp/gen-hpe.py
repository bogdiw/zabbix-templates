#!/usr/bin/env python3
"""Zabbix 7.2 template for HPE Aruba Instant On 1830 (JL814A) by SNMP.
Live-probed: sysObjectID=enterprises.11.2.3.7.11.210, ifNumber=71, sysDescr identifies
'HPE Networking Instant On Switch 48p Gigabit 4p SFP 1830 JL814A'.
Built on standard SNMPv2-MIB + IF-MIB (HPE proprietary CPU/temp not publicly documented for this model)."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-000000000003")
def U(key):
    u = uuid.uuid5(NS, key); b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

TPL = "HPE Aruba Instant On 1830 by SNMP"

SCALARS = [
    ("system.descr",   "System: Description",     "1.3.6.1.2.1.1.1.0", "", "CHAR"),
    ("system.objectid","System: Object ID",       "1.3.6.1.2.1.1.2.0", "", "CHAR"),
    ("system.uptime",  "System: Uptime",          "1.3.6.1.2.1.1.3.0", "uptime", "FLOAT", [("MULTIPLIER","0.01")]),
    ("system.contact", "System: Contact",         "1.3.6.1.2.1.1.4.0", "", "CHAR"),
    ("system.name",    "System: Name",            "1.3.6.1.2.1.1.5.0", "", "CHAR"),
    ("system.location","System: Location",        "1.3.6.1.2.1.1.6.0", "", "CHAR"),
    ("net.if.count",   "Network: Interface count","1.3.6.1.2.1.2.1.0", "", "UNSIGNED"),
]

def build():
    items = []
    for row in SCALARS:
        key, name, oid, units, vt = row[:5]
        prep = row[5] if len(row) > 5 else None
        item = {
            "uuid": U(f"item:{key}"), "name": name, "type": "SNMP_AGENT",
            "snmp_oid": oid, "key": key, "delay": "1m",
            "history": "31d", "trends": "365d" if vt != "CHAR" else "0",
            "value_type": vt,
            "tags": [{"tag":"class","value":"network"},{"tag":"vendor","value":"hpe"}],
        }
        if units: item["units"] = units
        if prep: item["preprocessing"] = [{"type":t,"parameters":[p]} for t,p in prep]
        items.append(item)

    # Interface LLD via IF-MIB
    if_proto = [
        {"uuid":U("proto:ifOperStatus"),"name":"Interface {#IFNAME}: Operational status",
         "type":"SNMP_AGENT","snmp_oid":"1.3.6.1.2.1.2.2.1.8.{#SNMPINDEX}",
         "key":"net.if.status[{#SNMPINDEX}]","delay":"1m","history":"31d","trends":"0",
         "value_type":"UNSIGNED","valuemap":{"name":"IF-MIB ifOperStatus"},
         "tags":[{"tag":"class","value":"network"},{"tag":"interface","value":"{#IFNAME}"}],
         "trigger_prototypes":[{"uuid":U("triggerproto:ifdown"),
            "expression":f"last(/{TPL}/net.if.status[{{#SNMPINDEX}}])=2 and last(/{TPL}/net.if.adminstatus[{{#SNMPINDEX}}])=1",
            "name":"Interface {#IFNAME} is down on {HOST.NAME}","priority":"AVERAGE"}]},
        {"uuid":U("proto:ifAdminStatus"),"name":"Interface {#IFNAME}: Admin status",
         "type":"SNMP_AGENT","snmp_oid":"1.3.6.1.2.1.2.2.1.7.{#SNMPINDEX}",
         "key":"net.if.adminstatus[{#SNMPINDEX}]","delay":"5m","history":"31d","trends":"0",
         "value_type":"UNSIGNED","valuemap":{"name":"IF-MIB ifAdminStatus"},
         "tags":[{"tag":"class","value":"network"},{"tag":"interface","value":"{#IFNAME}"}]},
        {"uuid":U("proto:ifInOctets"),"name":"Interface {#IFNAME}: In bits/s",
         "type":"SNMP_AGENT","snmp_oid":"1.3.6.1.2.1.31.1.1.1.6.{#SNMPINDEX}",
         "key":"net.if.in[{#SNMPINDEX}]","delay":"1m","history":"31d","trends":"365d",
         "value_type":"FLOAT","units":"bps",
         "preprocessing":[{"type":"CHANGE_PER_SECOND","parameters":[""]},{"type":"MULTIPLIER","parameters":["8"]}],
         "tags":[{"tag":"class","value":"network"},{"tag":"interface","value":"{#IFNAME}"}]},
        {"uuid":U("proto:ifOutOctets"),"name":"Interface {#IFNAME}: Out bits/s",
         "type":"SNMP_AGENT","snmp_oid":"1.3.6.1.2.1.31.1.1.1.10.{#SNMPINDEX}",
         "key":"net.if.out[{#SNMPINDEX}]","delay":"1m","history":"31d","trends":"365d",
         "value_type":"FLOAT","units":"bps",
         "preprocessing":[{"type":"CHANGE_PER_SECOND","parameters":[""]},{"type":"MULTIPLIER","parameters":["8"]}],
         "tags":[{"tag":"class","value":"network"},{"tag":"interface","value":"{#IFNAME}"}]},
    ]
    discovery_rules = [{
        "uuid": U("lld:if"),
        "name": "Network interfaces discovery",
        "type": "SNMP_AGENT",
        "snmp_oid": "discovery[{#IFNAME},1.3.6.1.2.1.31.1.1.1.1]",
        "key": "net.if.discovery",
        "delay": "5m",
        "filter": {"evaltype":"AND","conditions":[
            {"macro":"{#IFNAME}","value":"^(lo|null|sit\\d+)$","operator":"NOT_MATCHES_REGEX","formulaid":"A"}
        ]},
        "item_prototypes": if_proto,
    }]

    triggers = [{
        "uuid": U("trig:reboot"),
        "expression": f"last(/{TPL}/system.uptime)<10m",
        "name": "Switch was restarted on {HOST.NAME}",
        "priority": "INFO",
    }]

    return {"zabbix_export": {
        "version":"7.2",
        "template_groups":[{"uuid":U("tg:hvac"),"name":"Templates/HVAC"}],
        "templates":[{
            "uuid": U("tpl:hpe-aruba-1830"),
            "template": TPL, "name": TPL,
            "description":"HPE Aruba Instant On 1830 (JL814A and family) via SNMPv2c. Generic IF-MIB + SNMPv2-MIB; no HPE proprietary OIDs (Instant On line lacks public CPU/temp MIB). Set {$SNMP_COMMUNITY}.",
            "groups":[{"name":"Templates/HVAC"}],
            "items":items,
            "discovery_rules":discovery_rules,
            "valuemaps":[
                {"uuid":U("vm:ifOperStatus"),"name":"IF-MIB ifOperStatus","mappings":[
                    {"value":"1","newvalue":"up"},{"value":"2","newvalue":"down"},{"value":"3","newvalue":"testing"},
                    {"value":"4","newvalue":"unknown"},{"value":"5","newvalue":"dormant"},
                    {"value":"6","newvalue":"notPresent"},{"value":"7","newvalue":"lowerLayerDown"}]},
                {"uuid":U("vm:ifAdminStatus"),"name":"IF-MIB ifAdminStatus","mappings":[
                    {"value":"1","newvalue":"up"},{"value":"2","newvalue":"down"},{"value":"3","newvalue":"testing"}]},
            ],
            "macros":[{"macro":"{$SNMP_COMMUNITY}","value":"public","description":"SNMPv2c community"}],
        }],
        "triggers":triggers,
    }}

if __name__ == "__main__":
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
