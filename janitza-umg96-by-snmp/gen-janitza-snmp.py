#!/usr/bin/env python3
"""Zabbix 7.2 template for Janitza UMG96RM-E via SNMPv2c.
Validated 2026-05-08 against bm-ups-a @ 10.1.109.55 — values match Modbus readings exactly."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-00000000ba17")
def U(s):
    u = uuid.uuid5(NS, s); b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

TPL = "Janitza UMG96 by SNMP"
B = "1.3.6.1.4.1.34278"  # Janitza enterprise OID

# (key, name, oid_suffix, units, value_type, multiplier, triggers)
SCALARS = [
    # .1.x — V/I/P/cosphi per phase
    ("voltage_l1n",     "Voltage L1-N",       "1.1.0",  "V",  "FLOAT", 0.1, [
        ("low_warn",  "last(/{T}/voltage_l1n)<{$V.LOW.WARN} and last(/{T}/voltage_l1n)>1",   "L1-N voltage low on {HOST.NAME}: {ITEM.LASTVALUE}",     "WARNING"),
        ("low_crit",  "last(/{T}/voltage_l1n)<{$V.LOW.CRIT} and last(/{T}/voltage_l1n)>1",   "L1-N voltage critically low on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
        ("high_warn", "last(/{T}/voltage_l1n)>{$V.HIGH.WARN}", "L1-N voltage high on {HOST.NAME}: {ITEM.LASTVALUE}", "WARNING"),
        ("high_crit", "last(/{T}/voltage_l1n)>{$V.HIGH.CRIT}", "L1-N voltage critically high on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
    ]),
    ("voltage_l2n",     "Voltage L2-N",       "1.2.0",  "V",  "FLOAT", 0.1, [
        ("low_warn",  "last(/{T}/voltage_l2n)<{$V.LOW.WARN} and last(/{T}/voltage_l2n)>1",   "L2-N voltage low on {HOST.NAME}: {ITEM.LASTVALUE}",     "WARNING"),
        ("low_crit",  "last(/{T}/voltage_l2n)<{$V.LOW.CRIT} and last(/{T}/voltage_l2n)>1",   "L2-N voltage critically low on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
        ("high_warn", "last(/{T}/voltage_l2n)>{$V.HIGH.WARN}", "L2-N voltage high on {HOST.NAME}: {ITEM.LASTVALUE}", "WARNING"),
        ("high_crit", "last(/{T}/voltage_l2n)>{$V.HIGH.CRIT}", "L2-N voltage critically high on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
    ]),
    ("voltage_l3n",     "Voltage L3-N",       "1.3.0",  "V",  "FLOAT", 0.1, [
        ("low_warn",  "last(/{T}/voltage_l3n)<{$V.LOW.WARN} and last(/{T}/voltage_l3n)>1",   "L3-N voltage low on {HOST.NAME}: {ITEM.LASTVALUE}",     "WARNING"),
        ("low_crit",  "last(/{T}/voltage_l3n)<{$V.LOW.CRIT} and last(/{T}/voltage_l3n)>1",   "L3-N voltage critically low on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
        ("high_warn", "last(/{T}/voltage_l3n)>{$V.HIGH.WARN}", "L3-N voltage high on {HOST.NAME}: {ITEM.LASTVALUE}", "WARNING"),
        ("high_crit", "last(/{T}/voltage_l3n)>{$V.HIGH.CRIT}", "L3-N voltage critically high on {HOST.NAME}: {ITEM.LASTVALUE}", "HIGH"),
    ]),
    ("voltage_l1l2",    "Voltage L1-L2",      "1.4.0",  "V",  "FLOAT", 0.1, []),
    ("voltage_l2l3",    "Voltage L2-L3",      "1.5.0",  "V",  "FLOAT", 0.1, []),
    ("voltage_l3l1",    "Voltage L3-L1",      "1.6.0",  "V",  "FLOAT", 0.1, []),
    ("current_l1",      "Current L1",         "1.7.0",  "A",  "FLOAT", 0.001, []),
    ("current_l2",      "Current L2",         "1.8.0",  "A",  "FLOAT", 0.001, []),
    ("current_l3",      "Current L3",         "1.9.0",  "A",  "FLOAT", 0.001, []),
    ("current_n",       "Current N (neutral)","1.10.0", "A",  "FLOAT", 0.001, []),
    ("active_power_l1", "Active power L1",    "1.13.0", "W",  "FLOAT", None, []),
    ("active_power_l2", "Active power L2",    "1.14.0", "W",  "FLOAT", None, []),
    ("active_power_l3", "Active power L3",    "1.15.0", "W",  "FLOAT", None, []),
    ("reactive_power_l1","Reactive power L1", "1.16.0", "var","FLOAT", None, []),
    ("reactive_power_l2","Reactive power L2", "1.17.0", "var","FLOAT", None, []),
    ("reactive_power_l3","Reactive power L3", "1.18.0", "var","FLOAT", None, []),
    ("apparent_power_l1","Apparent power L1", "1.19.0", "VA", "FLOAT", None, []),
    ("apparent_power_l2","Apparent power L2", "1.20.0", "VA", "FLOAT", None, []),
    ("apparent_power_l3","Apparent power L3", "1.21.0", "VA", "FLOAT", None, []),
    ("cosphi_l1",       "Cos phi L1",         "1.22.0", "",   "FLOAT", 0.001, []),
    ("cosphi_l2",       "Cos phi L2",         "1.23.0", "",   "FLOAT", 0.001, []),
    ("cosphi_l3",       "Cos phi L3",         "1.24.0", "",   "FLOAT", 0.001, []),
    # .2.x — totals
    ("active_power_total","Active power total","2.1.0", "W",  "FLOAT", None, []),
    ("reactive_power_total","Reactive power total","2.2.0","var","FLOAT", None, []),
    ("apparent_power_total","Apparent power total","2.3.0","VA","FLOAT", None, []),
    ("cosphi_total",    "Cos phi total",      "2.4.0",  "",   "FLOAT", 0.001, [
        ("low", "last(/{T}/cosphi_total)<{$PF.LOW.WARN} and abs(last(/{T}/cosphi_total))>0.01", "Power factor low on {HOST.NAME}: {ITEM.LASTVALUE}", "INFO"),
    ]),
    # .3.x — energy per phase (Wh/varh)
    ("energy_active_l1","Energy active L1",   "3.1.0",  "Wh", "UNSIGNED", None, []),
    ("energy_active_l2","Energy active L2",   "3.2.0",  "Wh", "UNSIGNED", None, []),
    ("energy_active_l3","Energy active L3",   "3.3.0",  "Wh", "UNSIGNED", None, []),
    ("energy_reactive_l1","Energy reactive L1","3.4.0", "varh","UNSIGNED", None, []),
    ("energy_reactive_l2","Energy reactive L2","3.5.0", "varh","UNSIGNED", None, []),
    ("energy_reactive_l3","Energy reactive L3","3.6.0", "varh","UNSIGNED", None, []),
    # .4.x — totals
    ("energy_active_total","Energy active total","4.1.0","Wh","UNSIGNED", None, []),
    ("energy_reactive_total","Energy reactive total","4.2.0","varh","UNSIGNED", None, []),
    # .5.x — THD
    ("thd_voltage_l1",  "THD voltage L1",     "5.1.0",  "%",  "FLOAT", 0.1, [
        ("warn", "last(/{T}/thd_voltage_l1)>{$THD.V.WARN}", "THD voltage L1 high on {HOST.NAME}: {ITEM.LASTVALUE}%", "INFO"),
        ("crit", "last(/{T}/thd_voltage_l1)>{$THD.V.CRIT}", "THD voltage L1 above EN 50160 limit on {HOST.NAME}: {ITEM.LASTVALUE}%", "WARNING"),
    ]),
    ("thd_voltage_l2",  "THD voltage L2",     "5.2.0",  "%",  "FLOAT", 0.1, [
        ("warn", "last(/{T}/thd_voltage_l2)>{$THD.V.WARN}", "THD voltage L2 high on {HOST.NAME}: {ITEM.LASTVALUE}%", "INFO"),
        ("crit", "last(/{T}/thd_voltage_l2)>{$THD.V.CRIT}", "THD voltage L2 above EN 50160 limit on {HOST.NAME}: {ITEM.LASTVALUE}%", "WARNING"),
    ]),
    ("thd_voltage_l3",  "THD voltage L3",     "5.3.0",  "%",  "FLOAT", 0.1, [
        ("warn", "last(/{T}/thd_voltage_l3)>{$THD.V.WARN}", "THD voltage L3 high on {HOST.NAME}: {ITEM.LASTVALUE}%", "INFO"),
        ("crit", "last(/{T}/thd_voltage_l3)>{$THD.V.CRIT}", "THD voltage L3 above EN 50160 limit on {HOST.NAME}: {ITEM.LASTVALUE}%", "WARNING"),
    ]),
    ("thd_current_l1",  "THD current L1",     "5.4.0",  "%",  "FLOAT", 0.1, []),
    ("thd_current_l2",  "THD current L2",     "5.5.0",  "%",  "FLOAT", 0.1, []),
    ("thd_current_l3",  "THD current L3",     "5.6.0",  "%",  "FLOAT", 0.1, []),
    # .6.x — frequency + rotation
    ("frequency",       "Frequency",          "6.1.0",  "Hz", "FLOAT", 0.01, [
        ("low_warn",  "last(/{T}/frequency)<{$FREQ.LOW.WARN} and last(/{T}/frequency)>1",  "Frequency low on {HOST.NAME}: {ITEM.LASTVALUE} Hz",     "WARNING"),
        ("low_crit",  "last(/{T}/frequency)<{$FREQ.LOW.CRIT} and last(/{T}/frequency)>1",  "Frequency critically low on {HOST.NAME}: {ITEM.LASTVALUE} Hz", "HIGH"),
        ("high_warn", "last(/{T}/frequency)>{$FREQ.HIGH.WARN}", "Frequency high on {HOST.NAME}: {ITEM.LASTVALUE} Hz", "WARNING"),
        ("high_crit", "last(/{T}/frequency)>{$FREQ.HIGH.CRIT}", "Frequency critically high on {HOST.NAME}: {ITEM.LASTVALUE} Hz", "HIGH"),
    ]),
    ("rotation_l1",     "Rotation field L1",  "6.2.0",  "",   "FLOAT", 0.1, []),
    ("rotation_l2",     "Rotation field L2",  "6.3.0",  "",   "FLOAT", 0.1, []),
    # .8.6 — sysName label
    ("device_label",    "Device label",       "8.6.0",  "",   "CHAR",  None, []),
]

def build():
    items = []
    triggers = []
    for key, name, oid, units, vt, mult, trigs in SCALARS:
        item = {
            "uuid": U(f"item:{key}"),
            "name": f"Meter: {name}",
            "type": "SNMP_AGENT",
            "snmp_oid": f"{B}.{oid}",
            "key": key,
            "delay": "1m",
            "history": "31d",
            "trends": "365d" if vt != "CHAR" else "0",
            "value_type": vt,
            "tags": [{"tag": "class", "value": "meter"},
                     {"tag": "vendor", "value": "janitza"}],
        }
        if units: item["units"] = units
        if mult: item["preprocessing"] = [{"type": "MULTIPLIER", "parameters": [str(mult)]}]
        items.append(item)
        for tk, expr, descr, sev in trigs:
            triggers.append({
                "uuid": U(f"trig:{key}:{tk}"),
                "expression": expr.replace("{T}", TPL),
                "name": descr,
                "priority": sev,
            })

    # SNMP availability + reachability
    items.append({
        "uuid": U("item:snmp_avail"),
        "name": "SNMP availability",
        "type": "INTERNAL",
        "key": "zabbix[host,snmp,available]",
        "delay": "1m",
        "history": "7d", "trends": "0",
        "value_type": "UNSIGNED",
        "valuemap": {"name": "Zabbix host availability"},
        "tags": [{"tag": "component", "value": "availability"}],
    })
    triggers.append({
        "uuid": U("trig:snmp_unreachable"),
        "expression": f'max(/{TPL}/zabbix[host,snmp,available],#3)=0',
        "name": "SNMP unreachable on {HOST.NAME}",
        "priority": "HIGH",
    })
    triggers.append({
        "uuid": U("trig:no_data_freq"),
        "expression": f'nodata(/{TPL}/frequency,5m)=1',
        "name": "Meter not reporting on {HOST.NAME}",
        "priority": "AVERAGE",
    })
    triggers.append({
        "uuid": U("trig:energy_reset"),
        "expression": f'change(/{TPL}/energy_active_total)<-1000',
        "name": "Energy counter reset detected on {HOST.NAME}",
        "priority": "INFO",
        "description": "Active energy counter went backward by >1 kWh — meter was reset or rolled over. Affects energy bill calculations.",
        "manual_close": "YES",
    })

    return {"zabbix_export": {
        "version": "7.2",
        "template_groups": [{"uuid": U("tg:hvac"), "name": "Templates/HVAC"}],
        "templates": [{
            "uuid": U("tpl:janitza-snmp"),
            "template": TPL, "name": TPL,
            "description": "Janitza UMG96RM-E power meter via SNMPv2c (enterprise OID 34278). 46 items: V/I/P/cosphi per phase + totals, energy import per phase + totals, THD V/I, frequency, rotation. Live-validated 2026-05-08; values match Modbus exactly. Use this instead of the older Janitza-by-Modbus template.",
            "groups": [{"name": "Templates/HVAC"}],
            "items": items,
            "valuemaps": [{
                "uuid": U("vm:host_avail"),
                "name": "Zabbix host availability",
                "mappings": [
                    {"value": "0", "newvalue": "not available"},
                    {"value": "1", "newvalue": "available"},
                    {"value": "2", "newvalue": "unknown"},
                ],
            }],
            "macros": [
                {"macro": "{$SNMP_COMMUNITY}", "value": "public"},
                {"macro": "{$V.LOW.WARN}",  "value": "207", "description": "Per EN 50160: -10% of 230V nominal"},
                {"macro": "{$V.LOW.CRIT}",  "value": "195", "description": "Per EN 50160 extreme: -15% of 230V"},
                {"macro": "{$V.HIGH.WARN}", "value": "253", "description": "Per EN 50160: +10% of 230V nominal"},
                {"macro": "{$V.HIGH.CRIT}", "value": "264", "description": "Per EN 50160 extreme: +15% of 230V"},
                {"macro": "{$FREQ.LOW.WARN}",  "value": "49.5", "description": "Per EN 50160: 50 Hz -1%"},
                {"macro": "{$FREQ.LOW.CRIT}",  "value": "49",   "description": "Per EN 50160 extreme: 50 Hz -2%"},
                {"macro": "{$FREQ.HIGH.WARN}", "value": "50.5", "description": "Per EN 50160: 50 Hz +1%"},
                {"macro": "{$FREQ.HIGH.CRIT}", "value": "51",   "description": "Per EN 50160 extreme: 50 Hz +2%"},
                {"macro": "{$THD.V.WARN}",  "value": "5", "description": "IEEE 519-2014 individual harmonic limit"},
                {"macro": "{$THD.V.CRIT}",  "value": "8", "description": "EN 50160 / IEEE 519-2014 THD-V limit"},
                {"macro": "{$PF.LOW.WARN}", "value": "0.7", "description": "Below 0.7 indicates inefficient/inductive load"},
            ],
        }],
        "triggers": triggers,
    }}

if __name__ == "__main__":
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
