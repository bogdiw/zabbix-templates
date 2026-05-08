#!/usr/bin/env python3
"""Generate Zabbix 7.2 template YAML for Eaton 93PM via XUPS-MIB."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-000000000001")
_cache = {}
def U(key):
    # Deterministic but UUIDv4-shaped (Zabbix requires v4): take uuid5 hash, force version=4 + variant bits
    if key in _cache: return _cache[key]
    u = uuid.uuid5(NS, key)
    b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40  # version 4
    b[8] = (b[8] & 0x3F) | 0x80  # variant 10
    _cache[key] = uuid.UUID(bytes=bytes(b)).hex
    return _cache[key]

# (key, name, oid, units, value_type, valuemap, preprocessing, triggers)
SCALARS = [
    # Ident
    ("ups.manufacturer",        "UPS: Manufacturer",          "1.3.6.1.4.1.534.1.1.1.0", "", "CHAR", None, None, []),
    ("ups.model",               "UPS: Model",                 "1.3.6.1.4.1.534.1.1.2.0", "", "CHAR", None, None, []),
    ("ups.fw_version",          "UPS: Firmware version",      "1.3.6.1.4.1.534.1.1.3.0", "", "CHAR", None, None, []),
    ("ups.oem_code",            "UPS: OEM code",              "1.3.6.1.4.1.534.1.1.4.0", "", "UNSIGNED", None, None, []),
    # Battery
    ("ups.battery.runtime_s",   "UPS Battery: Runtime",       "1.3.6.1.4.1.534.1.2.1.0", "s",  "UNSIGNED", None, None, [("low_runtime","last(/{TPL}/ups.battery.runtime_s)<300","UPS battery runtime under 5min on {HOST.NAME}","HIGH")]),
    ("ups.battery.voltage_v",   "UPS Battery: Voltage",       "1.3.6.1.4.1.534.1.2.2.0", "V",  "FLOAT", None, None, []),
    ("ups.battery.current_a",   "UPS Battery: Current",       "1.3.6.1.4.1.534.1.2.3.0", "A",  "FLOAT", None, None, []),
    ("ups.battery.capacity_pct","UPS Battery: Capacity",      "1.3.6.1.4.1.534.1.2.4.0", "%",  "UNSIGNED", None, None, [("low_capacity","last(/{TPL}/ups.battery.capacity_pct)<50","UPS battery below 50% on {HOST.NAME}","WARNING"),("crit_capacity","last(/{TPL}/ups.battery.capacity_pct)<20","UPS battery below 20% on {HOST.NAME}","HIGH")]),
    ("ups.battery.abm_status",  "UPS Battery: ABM status",    "1.3.6.1.4.1.534.1.2.5.0", "",   "UNSIGNED", "Eaton XUPS battery ABM status", None, [("discharging","last(/{TPL}/ups.battery.abm_status)=2","UPS on battery (discharging) on {HOST.NAME}","HIGH")]),
    # Input
    ("ups.input.frequency_dhz", "UPS Input: Frequency",       "1.3.6.1.4.1.534.1.3.1.0", "Hz", "FLOAT", None, [("MULTIPLIER","0.1")], []),
    ("ups.input.line_bads",     "UPS Input: Line deviations", "1.3.6.1.4.1.534.1.3.2.0", "",   "UNSIGNED", None, None, []),
    ("ups.input.num_phases",    "UPS Input: Number of phases","1.3.6.1.4.1.534.1.3.3.0", "",   "UNSIGNED", None, None, []),
    ("ups.input.source",        "UPS Input: Source",          "1.3.6.1.4.1.534.1.3.5.0", "",   "UNSIGNED", "Eaton XUPS input source", None, []),
    # Output
    ("ups.output.load_pct",     "UPS Output: Load",           "1.3.6.1.4.1.534.1.4.1.0", "%",  "UNSIGNED", None, None, [("high_load","last(/{TPL}/ups.output.load_pct)>80","UPS load above 80% on {HOST.NAME}","WARNING")]),
    ("ups.output.frequency_dhz","UPS Output: Frequency",      "1.3.6.1.4.1.534.1.4.2.0", "Hz", "FLOAT", None, [("MULTIPLIER","0.1")], []),
    ("ups.output.num_phases",   "UPS Output: Number of phases","1.3.6.1.4.1.534.1.4.3.0","",   "UNSIGNED", None, None, []),
    ("ups.output.source",       "UPS Output: Power source",   "1.3.6.1.4.1.534.1.4.5.0", "",   "UNSIGNED", "Eaton XUPS output source", None, [("not_normal","last(/{TPL}/ups.output.source)<>3","UPS output not normal on {HOST.NAME}","HIGH")]),
    # Bypass
    ("ups.bypass.frequency_dhz","UPS Bypass: Frequency",      "1.3.6.1.4.1.534.1.5.1.0", "Hz", "FLOAT", None, [("MULTIPLIER","0.1")], []),
    ("ups.bypass.num_phases",   "UPS Bypass: Number of phases","1.3.6.1.4.1.534.1.5.2.0","",   "UNSIGNED", None, None, []),
    # Environment
    ("ups.env.ambient_temp",    "UPS Env: Ambient temperature","1.3.6.1.4.1.534.1.6.1.0","°C","FLOAT", None, None, [("temp_high","last(/{TPL}/ups.env.ambient_temp)>35","UPS ambient temperature high on {HOST.NAME}","WARNING")]),
    ("ups.env.ambient_humidity","UPS Env: Ambient humidity",  "1.3.6.1.4.1.534.1.6.4.0", "%",  "UNSIGNED", None, None, []),
    # Alarm
    ("ups.alarm.active_count",  "UPS Alarm: Active alarms",   "1.3.6.1.4.1.534.1.7.1.0", "",   "UNSIGNED", None, None, [("any_alarm","last(/{TPL}/ups.alarm.active_count)>0","UPS has active alarms on {HOST.NAME}","HIGH")]),
    ("ups.alarm.event_count",   "UPS Alarm: Event count",     "1.3.6.1.4.1.534.1.7.18.0","",   "UNSIGNED", None, None, []),
    # Test
    ("ups.test.battery_status", "UPS Test: Battery test result","1.3.6.1.4.1.534.1.8.2.0","",  "UNSIGNED", "Eaton XUPS battery test status", None, [("battery_test_failed","last(/{TPL}/ups.test.battery_status)=3","UPS battery test failed on {HOST.NAME}","HIGH")]),
    # Config
    ("ups.config.output_voltage","UPS Config: Output voltage","1.3.6.1.4.1.534.1.10.1.0","V","UNSIGNED", None, None, []),
    ("ups.config.output_watts", "UPS Config: Output rated W", "1.3.6.1.4.1.534.1.10.3.0","W","UNSIGNED", None, None, []),
    # Topology
    ("ups.topology.type",       "UPS Topology: Type",         "1.3.6.1.4.1.534.1.13.1.0","","UNSIGNED", None, None, []),
]

VALUEMAPS = {
    "Eaton XUPS battery ABM status": [("1","Charging"),("2","Discharging"),("3","Floating"),("4","Resting"),("5","Unknown")],
    "Eaton XUPS input source":       [("1","None"),("2","Primary utility"),("3","Bypass"),("4","Secondary utility"),("5","Generator"),("6","Flywheel"),("7","Fuel cell")],
    "Eaton XUPS output source":      [("1","Other"),("2","None"),("3","Normal"),("4","Bypass"),("5","Battery"),("6","Booster"),("7","Reducer"),("8","Parallel capacity"),("9","Parallel redundant"),("10","High efficiency mode"),("11","Maintenance bypass"),("12","ESS")],
    "Eaton XUPS battery test status":[("1","Unknown"),("2","Passed"),("3","Failed"),("4","In progress"),("5","Not supported"),("6","Inhibited"),("7","Scheduled")],
}

TEMPLATE_NAME = "Eaton 93PM by SNMP"

def build():
    items = []
    triggers = []
    for key, name, oid, units, vtype, vmap, prep, trigs in SCALARS:
        item = {
            "uuid": U(f"item:{key}"),
            "name": name,
            "type": "SNMP_AGENT",
            "snmp_oid": oid,
            "key": key,
            "delay": "1m",
            "history": "31d",
            "trends": "365d" if vtype != "CHAR" else "0",
            "value_type": vtype,
            "tags": [{"tag":"class","value":"ups"},{"tag":"vendor","value":"eaton"}],
        }
        if units: item["units"] = units
        if vmap: item["valuemap"] = {"name": vmap}
        if prep:
            item["preprocessing"] = [{"type": t, "parameters": [p]} for t,p in prep]
        items.append(item)
        for tkey, expr, descr, sev in trigs:
            triggers.append({
                "uuid": U(f"trigger:{key}:{tkey}"),
                "expression": expr.replace("{TPL}", TEMPLATE_NAME),
                "name": descr,
                "priority": sev,
            })

    # Per-phase LLD discovery for input/output/bypass tables
    discovery_rules = []
    for tname, idx_oid, base_oid, walk_oid, fields, prefix in [
        ("Input phases", "1.3.6.1.4.1.534.1.3.4.1.1", "1.3.6.1.4.1.534.1.3.4.1", "1.3.6.1.4.1.534.1.3.4.1.1",
            [("voltage_v","Voltage","1.3.6.1.4.1.534.1.3.4.1.2","V","FLOAT"),
             ("current_a","Current","1.3.6.1.4.1.534.1.3.4.1.3","A","FLOAT"),
             ("watts_w","Active power","1.3.6.1.4.1.534.1.3.4.1.4","W","UNSIGNED")], "ups.input.phase"),
        ("Output phases", "1.3.6.1.4.1.534.1.4.4.1.1", "1.3.6.1.4.1.534.1.4.4.1", "1.3.6.1.4.1.534.1.4.4.1.1",
            [("voltage_v","Voltage","1.3.6.1.4.1.534.1.4.4.1.2","V","FLOAT"),
             ("current_a","Current","1.3.6.1.4.1.534.1.4.4.1.3","A","FLOAT"),
             ("watts_w","Active power","1.3.6.1.4.1.534.1.4.4.1.4","W","UNSIGNED")], "ups.output.phase"),
        ("Bypass phases", "1.3.6.1.4.1.534.1.5.3.1.1", "1.3.6.1.4.1.534.1.5.3.1", "1.3.6.1.4.1.534.1.5.3.1.1",
            [("voltage_v","Voltage","1.3.6.1.4.1.534.1.5.3.1.2","V","FLOAT")], "ups.bypass.phase"),
    ]:
        item_proto = []
        for f, fname, foid, units, vtype in fields:
            item_proto.append({
                "uuid": U(f"proto:{prefix}:{f}"),
                "name": f"{tname.split()[0]} phase {{#PHASE}}: {fname}",
                "type": "SNMP_AGENT",
                "snmp_oid": f"{foid}.{{#SNMPINDEX}}",
                "key": f"{prefix}.{f}[{{#SNMPINDEX}}]",
                "delay": "1m",
                "history": "31d", "trends": "365d",
                "value_type": vtype,
                "units": units,
                "tags": [{"tag":"class","value":"ups"},{"tag":"vendor","value":"eaton"},{"tag":"phase","value":"{#PHASE}"}],
            })
        discovery_rules.append({
            "uuid": U(f"lld:{tname}"),
            "name": f"{tname} discovery",
            "type": "SNMP_AGENT",
            "snmp_oid": f"discovery[{{#PHASE}},{idx_oid}]",
            "key": f"{prefix}.discovery",
            "delay": "5m",
            "item_prototypes": item_proto,
        })

    # Env contact LLD
    env_proto = [
        {"uuid": U("proto:env_contact:type"),"name":"Env contact {#INDEX}: Type","type":"SNMP_AGENT","snmp_oid":"1.3.6.1.4.1.534.1.6.8.1.2.{#SNMPINDEX}","key":"ups.env.contact.type[{#SNMPINDEX}]","delay":"1m","history":"31d","trends":"0","value_type":"UNSIGNED","tags":[{"tag":"class","value":"ups"}]},
        {"uuid": U("proto:env_contact:state"),"name":"Env contact {#INDEX}: State","type":"SNMP_AGENT","snmp_oid":"1.3.6.1.4.1.534.1.6.8.1.3.{#SNMPINDEX}","key":"ups.env.contact.state[{#SNMPINDEX}]","delay":"1m","history":"31d","trends":"0","value_type":"UNSIGNED","tags":[{"tag":"class","value":"ups"}]},
        {"uuid": U("proto:env_contact:descr"),"name":"Env contact {#INDEX}: Description","type":"SNMP_AGENT","snmp_oid":"1.3.6.1.4.1.534.1.6.8.1.4.{#SNMPINDEX}","key":"ups.env.contact.descr[{#SNMPINDEX}]","delay":"5m","history":"31d","trends":"0","value_type":"CHAR","tags":[{"tag":"class","value":"ups"}]},
    ]
    discovery_rules.append({
        "uuid": U("lld:env_contacts"),
        "name": "Environment contacts discovery",
        "type": "SNMP_AGENT",
        "snmp_oid": "discovery[{#INDEX},1.3.6.1.4.1.534.1.6.8.1.1]",
        "key": "ups.env.contacts.discovery",
        "delay": "5m",
        "item_prototypes": env_proto,
    })

    # SNMP availability item + trigger (consistent with other HVAC templates)
    items.append({
        "uuid": U("item:snmp_avail"),
        "name": "SNMP availability",
        "type": "INTERNAL",
        "key": "zabbix[host,snmp,available]",
        "delay": "1m",
        "history": "7d", "trends": "0",
        "value_type": "UNSIGNED",
        "valuemap": {"name": "Zabbix host availability"},
        "tags": [{"tag":"component","value":"availability"}],
    })
    triggers.append({
        "uuid": U("trig:snmp_unreachable"),
        "expression": f'max(/{TEMPLATE_NAME}/zabbix[host,snmp,available],#3)=0',
        "name": "SNMP unreachable on {HOST.NAME}",
        "priority": "HIGH",
    })
    VALUEMAPS["Zabbix host availability"] = [("0","not available"),("1","available"),("2","unknown")]

    tpl = {
        "zabbix_export": {
            "version": "7.2",
            "template_groups": [{"uuid": U("tg:hvac"), "name": "Templates/HVAC"}],
            "templates": [{
                "uuid": U("tpl:eaton-93pm"),
                "template": TEMPLATE_NAME,
                "name": TEMPLATE_NAME,
                "description": "Eaton 93PM-G2 (and other XUPS-MIB-compatible UPS) via SNMPv2c. Mirror of cloudxedge Telegraf XUPS field set, validated against ups-a-pl/ups-b-pl @ Brazi.",
                "groups": [{"name": "Templates/HVAC"}],
                "items": items,
                "discovery_rules": discovery_rules,
                "valuemaps": [
                    {"uuid": U(f"vm:{k}"), "name": k, "mappings":[{"value":v,"newvalue":n} for v,n in vals]}
                    for k, vals in VALUEMAPS.items()
                ],
                "macros": [
                    {"macro":"{$SNMP_COMMUNITY}","value":"public","description":"SNMPv2c community string"},
                ],
            }],
            "triggers": triggers,
        }
    }
    return tpl

if __name__ == "__main__":
    import json
    yaml.Dumper.ignore_aliases = lambda *a: True
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
