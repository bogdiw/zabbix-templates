#!/usr/bin/env python3
"""Zabbix 7.2 template for ComAp InteliLite NT (AMF26-P and family) via Modbus TCP.
Uses standard fixed register addresses from InteliCommunication Guide.
Polls via passive Zabbix Agent 2 'modbus.get' — point host's Agent interface at
zabbix-agent2-modbus.hvac.svc:10050 (Service ClusterIP)."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-00000000ca01")
def U(s):
    u = uuid.uuid5(NS, s); b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

TPL = "ComAp InteliLite by Modbus"

# (key_suffix, name, register_addr, datatype, units, multiplier, sentinel_filter, triggers)
REGS = [
    # Setup (mostly static — useful for inventory)
    ("nominal_power",    "Nominal power",       8276, "uint16", "kW",  None, False, []),
    ("nominal_current",  "Nominal current",     8275, "uint16", "A",   None, False, []),
    ("nominal_voltage",  "Nominal voltage L-N", 8277, "uint16", "V",   None, False, []),
    ("nominal_freq",     "Nominal frequency",   8278, "uint16", "Hz",  None, False, []),
    ("nominal_rpm",      "Nominal RPM",         8252, "uint16", "RPM", None, False, []),
    ("controller_mode",  "Controller mode",     8315, "uint16", "",    None, False, [
        ("notauto", "last(/{T}/controller_mode)<>2", "Generator NOT in AUTO mode on {HOST.NAME}: {ITEM.LASTVALUE}", "WARNING"),
    ]),
    # Engine
    ("engine_rpm",       "Engine RPM",          8253, "uint16", "RPM", None, False, []),
    ("coolant_temp",     "Coolant temperature", 8227, "int16",  "°C",  None, True,  [
        ("high",  "last(/{T}/coolant_temp)>{$COOLANT.HIGH}",  "Coolant temp high on {HOST.NAME}: {ITEM.LASTVALUE} °C", "HIGH"),
    ]),
    ("fuel_level",       "Fuel level",          8228, "int16",  "%",   None, True, [
        ("low",   "last(/{T}/fuel_level)<{$FUEL.LOW} and last(/{T}/fuel_level)>=0", "Fuel level low on {HOST.NAME}: {ITEM.LASTVALUE}%", "WARNING"),
    ]),
    ("run_hours",        "Run hours",           8229, "uint16", "h",   None, False, []),
    # Generator electrical (only registers confirmed live on this controller)
    ("gen_current_l1",   "Gen current L1",      8202, "uint16", "A",   None, False, []),
    ("gen_current_l2",   "Gen current L2",      8203, "uint16", "A",   None, False, []),
    ("gen_current_l3",   "Gen current L3",      8204, "uint16", "A",   None, False, []),
    ("gen_power_total",  "Gen active power",    8205, "int16",  "kW",  None, False, []),
    ("gen_apparent_total","Gen apparent power", 8208, "int16",  "kVA", None, False, []),
    ("gen_pf_total",     "Gen power factor",    8211, "int16",  "",    0.001, False, []),
    # Mains
    ("mains_freq",       "Mains frequency",     8210, "uint16", "Hz",  0.1, False, []),
    ("mains_voltage_l1", "Mains voltage L1",    8213, "uint16", "V",   None, False, []),
    # Energy
    ("energy_kwh_lsb",   "Energy total kWh",    8200, "uint16", "kWh", None, False, []),
    # Binary inputs (status/alarm bits — meaning depends on programmer config)
    ("bin2",             "Binary inputs word 2",8301, "uint16", "",    None, False, []),
    ("bin3",             "Binary inputs word 3",8302, "uint16", "",    None, False, []),
    ("bin4",             "Binary inputs word 4",8303, "uint16", "",    None, False, []),
]
# Removed (illegal data address on this firmware/config):
#   8201 (energy MSB), 8214/8215 (mains V L2/L3), 8226 (oil pressure),
#   8230 (battery voltage), 8240 (gen freq), 8242-8244 (gen V L1/L2/L3),
#   8300 (BIN1), 8500/8501 (alarm words)
# These can be added back once the gen-set commissioner exposes them via User Modbus.

# ComAp signed-int16 sentinel for "sensor not connected" — both +/-32768
SENTINEL = "-?32768"

def build():
    items = []
    triggers = []
    for key, name, addr, dtype, units, mult, filter_sentinel, trigs in REGS:
        item = {
            "uuid": U(f"item:{key}"),
            "name": f"Generator: {name}",
            # Passive Zabbix agent: type field omitted (default in YAML)
            "key": f'modbus.get[{{$MODBUS.ENDPOINT}},{{$MODBUS.SLAVE}},3,{addr},1,{dtype}]',
            "delay": "1m",
            "history": "31d",
            "trends": "365d" if dtype != "" else "0",
            "value_type": "FLOAT" if mult else ("UNSIGNED" if dtype.startswith("uint") else "FLOAT"),
            "tags": [{"tag": "class", "value": "generator"},
                     {"tag": "vendor", "value": "comap"}],
        }
        if units: item["units"] = units
        prep = []
        if filter_sentinel:
            prep.append({"type":"MATCHES_REGEX","parameters":[f"^(?!{SENTINEL}$).*$"],"error_handler":"DISCARD_VALUE"})
        if mult:
            prep.append({"type":"MULTIPLIER","parameters":[str(mult)]})
        if prep: item["preprocessing"] = prep
        items.append(item)

        # rebuild trigger expressions to use the actual modbus.get key
        full_key = f'modbus.get[{{$MODBUS.ENDPOINT}},{{$MODBUS.SLAVE}},3,{addr},1,{dtype}]'
        for tk, expr, descr, sev in trigs:
            # replace bare item key with full key in expression
            ex = expr.replace(f"/{{T}}/{key}", f"/{{T}}/{full_key}").replace("{T}", TPL)
            triggers.append({
                "uuid": U(f"trig:{key}:{tk}"),
                "expression": ex,
                "name": descr,
                "priority": sev,
            })

    # Engine running detection
    rpm_key = 'modbus.get[{$MODBUS.ENDPOINT},{$MODBUS.SLAVE},3,8253,1,uint16]'
    triggers.append({
        "uuid": U("trig:engine_running"),
        "expression": f'last(/{TPL}/{rpm_key})>500',
        "name": "Generator running on {HOST.NAME}",
        "priority": "INFO",
        "description": "Engine RPM above 500 — generator is supplying load (or warming up).",
    })

    return {"zabbix_export": {
        "version": "7.2",
        "template_groups": [{"uuid": U("tg:hvac"), "name": "Templates/HVAC"}],
        "templates": [{
            "uuid": U("tpl:comap"),
            "template": TPL, "name": TPL,
            "description": "ComAp InteliLite NT AMF26-P (and family) generator controller via Modbus TCP. Polls fixed standard addresses (engine, generator electrical, mains, alarms). Requires a passive Zabbix Agent 2 with the modbus plugin (the zabbix-agent2-modbus deployment in hvac ns at 10050). Set host's Agent interface to that service. Set {$MODBUS.ENDPOINT} = tcp://<gen-ip>:502 and {$MODBUS.SLAVE} = 1.",
            "groups": [{"name": "Templates/HVAC"}],
            "items": items,
            "macros": [
                {"macro": "{$MODBUS.ENDPOINT}", "value": "tcp://10.1.109.53:502", "description": "Modbus TCP endpoint URL of the generator IB-Lite"},
                {"macro": "{$MODBUS.SLAVE}", "value": "1", "description": "Modbus unit ID — typically 1 for InteliLite NT"},
                {"macro": "{$COOLANT.HIGH}", "value": "95", "description": "Coolant temp high alarm threshold (°C)"},
                {"macro": "{$OIL.LOW}", "value": "1.5", "description": "Oil pressure low alarm threshold (bar)"},
                {"macro": "{$FUEL.LOW}", "value": "20", "description": "Fuel level low warn threshold (%)"},
                {"macro": "{$BATT.LOW}", "value": "11.5", "description": "Battery voltage low alarm threshold (V)"},
            ],
        }],
        "triggers": triggers,
    }}

if __name__ == "__main__":
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
