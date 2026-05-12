#!/usr/bin/env python3
"""Zabbix 7.2 template for ComAp InteliLite NT AMF26P via Modbus TCP.

Uses ComAp Com.Obj. addresses (NOT LiteEdit 40001-format) — verified against the
official GSW 225I.TXT register map and a working zabbix-agent2-modbus poller.
Polled via passive Zabbix Agent 2 `modbus.get` (zabbix-agent2-modbus.hvac.svc:10050).

Set on each host:
  {$MODBUS.ENDPOINT} = tcp://<gen-ip>:502
  {$MODBUS.SLAVE}    = 1
"""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-00000000ca02")
def U(s):
    u = uuid.uuid5(NS, s); b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

TPL = "ComAp InteliLite by Modbus"

# MINIMAL set — only items needed for triggers + a few for context.
# Full telemetry (114 fields) lives in InfluxDB via Telegraf; Zabbix Agent2's
# per-item TCP polling hits the IB-Lite 2-client limit when too many items are
# configured. Keep this lean — alerts only.
# (key, name, comobj, dtype, units, scale_mult, subsystem)
ITEMS = [
    # ── Status (gating for engine-mechanical alerts) ───────────────────────
    ("engine_state",      "Status: Engine state",           8330, "uint16", "",     None, "status"),
    ("engine_rpm",        "Engine: RPM",                    8209, "uint16", "RPM",  None, "engine"),
    ("bin_inputs",        "Status: Binary inputs",          8235, "uint16", "",     None, "status"),
    # ── Engine sensors (used by triggers) ──────────────────────────────────
    ("oil_pressure_bar",  "Engine: Oil pressure",           8227, "int16",  "Bar",  0.1,  "engine"),
    ("battery_voltage",   "Engine: Battery voltage",        8213, "int16",  "V",    0.1,  "engine"),
    ("fuel_level_pct",    "Engine: Fuel level",             8229, "int16",  "%",    None, "engine"),
    # ── Mains (used by trigger for mains-failure detection) ────────────────
    ("mains_voltage_l1n", "Mains: Voltage L1-N",            8195, "uint16", "V",    None, "mains"),
    ("mains_voltage_l2n", "Mains: Voltage L2-N",            8196, "uint16", "V",    None, "mains"),
    ("mains_voltage_l3n", "Mains: Voltage L3-N",            8197, "uint16", "V",    None, "mains"),
    # ── Generator electrical (used by triggers) ────────────────────────────
    ("earth_fault_a",     "Generator: Earth fault current", 8208, "uint16", "A",    0.01, "generator"),
    # ── ECU (used by coolant-temp trigger) ─────────────────────────────────
    ("ecu_coolant_temp_c","ECU: Coolant temp",              9855, "int16",  "°C",   None, "ecu"),
    # ── Statistics (counter triggers) ──────────────────────────────────────
    ("num_starts",        "Stats: Number of starts",        8207, "uint16", "",     None, "stats"),
    # ── Service timers (used by service-due trigger) ───────────────────────
    ("service_basic_h",   "Service: Basic countdown",      13853, "uint16", "h",    None, "service"),
    ("service_lvl2_h",    "Service: Level 2 countdown",    13854, "uint16", "h",    None, "service"),
    ("service_lvl3_h",    "Service: Level 3 countdown",    13855, "uint16", "h",    None, "service"),
    # ── Useful context items (NOT in triggers but shown on dashboards) ─────
    ("breaker_state",     "Status: Breaker state",          8455, "uint16", "",     None, "status"),
    ("gen_frequency",     "Generator: Frequency",           8210, "uint16", "Hz",   0.1,  "generator"),
    ("gen_power_total",   "Generator: Active power total",  8202, "int16",  "kW",   0.1,  "generator"),
]

# Triggers — engine_state gating prevents idle false positives.
# Table#1: Init=21 NotReady=22 Prestart=23 Cranking=24 Pause=25 Starting=26
# Running=27 Loaded=28 Stop=29 Shutdown=30 Ready=31 Cooling=32 EmergMan=33
# MainsOper=34 MainsFlt=35 MainsRet=37 AfterCool=46
TRIGGERS = [
    # ── DISASTER ───────────────────────────────────────────────────────────
    ("Generator: Modbus poller unreachable on {HOST.NAME}",
     'nodata(/{T}/engine_state,15m)=1', 'HIGH',
     'No Modbus data for 15 min. Could be IB-Lite client-limit contention or panel reboot. Genset itself may still be fine — Telegraf has independent visibility.'),
    ("Generator: Overspeed shutdown on {HOST.NAME}",
     'last(/{T}/engine_rpm)>({$GEN.NOMINAL.RPM}*{$GEN.OVERSPEED.PCT}/100)', 'DISASTER',
     'Engine speed exceeded {$GEN.OVERSPEED.PCT}% of nominal RPM. Mechanical risk.'),
    ("Generator: Low oil pressure while running on {HOST.NAME}",
     'last(/{T}/engine_state)>=27 and last(/{T}/engine_state)<=28 and last(/{T}/engine_rpm)>1200 and last(/{T}/oil_pressure_bar)<{$OIL.LOW.BAR}',
     'DISASTER',
     'Oil pressure {ITEM.LASTVALUE} bar < {$OIL.LOW.BAR} bar while engine running. Bearing seizure risk.'),
    ("Generator: Low coolant level on {HOST.NAME}",
     'bitand(last(/{T}/bin_inputs),4)=4', 'DISASTER',
     'Low coolant level sensor active (bin_inputs bit 2). NFPA 110 critical.'),
    ("Generator: Battery voltage critically low on {HOST.NAME}",
     'last(/{T}/battery_voltage)<{$BATT.LOW.CRIT} and last(/{T}/battery_voltage)>5', 'HIGH',
     'Battery {ITEM.LASTVALUE}V < {$BATT.LOW.CRIT}V. Cannot crank — genset may fail to start. Not in-flight emergency; downgraded from Disaster.'),
    # ── HIGH ───────────────────────────────────────────────────────────────
    ("Generator: Mains failure detected on {HOST.NAME}",
     'last(/{T}/mains_voltage_l1n)<({$GEN.NOMINAL.V.LN}*0.85) and last(/{T}/mains_voltage_l2n)<({$GEN.NOMINAL.V.LN}*0.85) and last(/{T}/mains_voltage_l3n)<({$GEN.NOMINAL.V.LN}*0.85)',
     'HIGH',
     'All 3 mains phases < 85% of nominal. AMF should start the genset.'),
    ("Generator: Earth fault current on {HOST.NAME}",
     'last(/{T}/earth_fault_a)>{$EARTH.FAULT.A}', 'HIGH',
     'Earth fault {ITEM.LASTVALUE}A > {$EARTH.FAULT.A}A. Insulation fault on alternator or load.'),
    ("Generator: Fuel level critically low on {HOST.NAME}",
     'last(/{T}/fuel_level_pct)<{$FUEL.LOW.CRIT.PCT} and last(/{T}/fuel_level_pct)>=0', 'HIGH',
     'Fuel {ITEM.LASTVALUE}% < {$FUEL.LOW.CRIT.PCT}% (NFPA 110 critical). Refill now.'),
    ("Generator: Battery low (engine stopped) on {HOST.NAME}",
     'last(/{T}/battery_voltage)<{$BATT.LOW.WARN} and last(/{T}/battery_voltage)>={$BATT.LOW.CRIT} and last(/{T}/engine_state)<24', 'HIGH',
     'Battery {ITEM.LASTVALUE}V (engine stopped). Charger may be failing.'),
    ("Generator: ECU coolant temperature high on {HOST.NAME}",
     'last(/{T}/ecu_coolant_temp_c)>{$COOLANT.HIGH.C} and last(/{T}/ecu_coolant_temp_c)<200', 'HIGH',
     'Coolant {ITEM.LASTVALUE}°C > {$COOLANT.HIGH.C}°C (only valid if J1939 ECU connected).'),
    ("Generator: Underspeed while loaded on {HOST.NAME}",
     'last(/{T}/engine_state)=28 and last(/{T}/engine_rpm)<({$GEN.NOMINAL.RPM}*{$GEN.UNDERSPEED.PCT}/100)', 'HIGH',
     'Engine RPM < {$GEN.UNDERSPEED.PCT}% of nominal while Loaded. Governor or fuel issue.'),
    # ── WARNING ────────────────────────────────────────────────────────────
    ("Generator: NOT in AUTO mode on {HOST.NAME}",
     'last(/{T}/engine_state)=22 or last(/{T}/engine_state)=21', 'WARNING',
     'Engine state Init/NotReady. Check controller mode switch — genset will not auto-start.'),
    ("Generator: Fuel level low on {HOST.NAME}",
     'last(/{T}/fuel_level_pct)<{$FUEL.LOW.WARN.PCT} and last(/{T}/fuel_level_pct)>={$FUEL.LOW.CRIT.PCT}', 'WARNING',
     'Fuel {ITEM.LASTVALUE}% < {$FUEL.LOW.WARN.PCT}%. Schedule refill.'),
    ("Generator: Battery overvoltage on {HOST.NAME}",
     'last(/{T}/battery_voltage)>{$BATT.HIGH}', 'WARNING',
     'Battery {ITEM.LASTVALUE}V > {$BATT.HIGH}V. Charger may be faulty.'),
    ("Generator: Service due (any timer critically low) on {HOST.NAME}",
     'last(/{T}/service_basic_h)<{$SERVICE.LOW.HOURS.CRIT} or last(/{T}/service_lvl2_h)<{$SERVICE.LOW.HOURS.CRIT} or last(/{T}/service_lvl3_h)<{$SERVICE.LOW.HOURS.CRIT}', 'WARNING',
     'A service interval has < {$SERVICE.LOW.HOURS.CRIT}h remaining. Schedule maintenance.'),
    ("Generator: Unscheduled run on {HOST.NAME}",
     'last(/{T}/engine_state)>=24 and last(/{T}/engine_state)<=28 and last(/{T}/mains_voltage_l1n)>({$GEN.NOMINAL.V.LN}*0.9)', 'WARNING',
     'Engine running while mains is healthy. Verify scheduled test or manual run.'),
    # ── INFORMATION ────────────────────────────────────────────────────────
    ("Generator: Cooling cycle active on {HOST.NAME}",
     'last(/{T}/engine_state)=32 or last(/{T}/engine_state)=46', 'INFO',
     'Engine in Cooling/AfterCool state. Cool-down sequence underway.'),
]

ENGINE_STATE_MAP = {
    21: "Init", 22: "NotReady", 23: "Prestart", 24: "Cranking", 25: "Pause",
    26: "Starting", 27: "Running", 28: "Loaded", 29: "Stop", 30: "Shutdown",
    31: "Ready", 32: "Cooling", 33: "EmergMan", 34: "MainsOper", 35: "MainsFlt",
    36: "IslOper", 37: "MainsRet", 38: "BrksOff", 39: "NoTimer", 40: "MCBClose",
    41: "ReturnDel", 42: "TransDel", 43: "IdleRun", 44: "MinStabTO",
    45: "MaxStabTO", 46: "AfterCool", 47: "GCBOpen", 48: "StopValve",
    49: "StartDel", 50: "1Ph", 51: "3PD", 52: "3PY", 53: "MRSMode",
}
BREAKER_STATE_MAP = {
    0: "Unknown", 1: "BothOpen", 2: "MainsClosed-GenOpen",
    3: "MainsOpen-GenClosed", 4: "BothClosedParallel",
    34: "ReadyStandby", 35: "MainsNormal", 36: "GenSupplyingLoad",
}

def build_item(key, name, comobj, dtype, units, scale, subsys):
    """Build a Zabbix HTTP Agent item that reads from InfluxDB via Flux query.
    The Modbus comobj/dtype/scale args are ignored — Telegraf already applies them
    on the Modbus side; we just read the already-scaled value from InfluxDB.
    """
    flux = (
        f'from(bucket:"hvac") |> range(start:-3m) '
        f'|> filter(fn:(r) => r._measurement=="generator" '
        f'and r.host=="{{$INFLUX.HOST}}" and r._field=="{key}") '
        f'|> last() |> keep(columns:["_value"])'
    )
    item = {
        "uuid": U(f"item-{key}"),
        "name": name,
        "type": "HTTP_AGENT",
        "key": f"influxdb.generator.{key}",
        "url": "{$INFLUX.URL}/api/v2/query",
        "query_fields": [{"name": "org", "value": "{$INFLUX.ORG}"}],
        "request_method": "POST",
        "post_type": "RAW",
        "posts": flux,
        "headers": [
            {"name": "Authorization", "value": "Token {$INFLUX.TOKEN}"},
            {"name": "Content-Type", "value": "application/vnd.flux"},
        ],
        "delay": "1m",
        "history": "31d",
        "trends": "365d",
        "value_type": "FLOAT",
        "units": units,
        "tags": [
            {"tag": "class", "value": "generator"},
            {"tag": "vendor", "value": "comap"},
            {"tag": "subsystem", "value": subsys},
            {"tag": "source", "value": "influxdb"},
        ],
        # Regex extracts numeric _value from Flux CSV response:
        #   ,result,table,_value
        #   ,_result,0,30
        "preprocessing": [
            {"type": "REGEX", "parameters": [",_result,\\d+,([-0-9.eE]+)", "\\1"]},
        ],
    }
    if key == "engine_state":
        item["valuemap"] = {"name": "ComAp Engine State"}
        item["value_type"] = "UNSIGNED"
    elif key == "breaker_state":
        item["valuemap"] = {"name": "ComAp Breaker State"}
        item["value_type"] = "UNSIGNED"
    return item

# Map logical names → actual item keys for trigger expression substitution
KEY_MAP = {key: f"influxdb.generator.{key}" for key, *_ in ITEMS}

def build_trigger(name, expr, severity, desc):
    e = expr.replace("{T}", TPL)
    # Replace /TPL/<key> with /TPL/<modbus.get[...]>
    import re
    def sub(m):
        tpl, key = m.group(1), m.group(2)
        return f"/{tpl}/{KEY_MAP.get(key, key)}"
    e = re.sub(r"/([^/]+)/([a-z_][a-z0-9_]*)", sub, e)
    return {
        "uuid": U(f"trigger-{name}"),
        "expression": e,
        "name": name,
        "priority": severity,
        "description": desc,
        "manual_close": "YES",
    }

template = {
    "zabbix_export": {
        "version": "7.2",
        "template_groups": [{"uuid": "e4ba987200b54b2a83f2050f6e71f0da", "name": "Templates/HVAC"}],
        "templates": [{
            "uuid": "7d03b41cfd1748b99c780497218d3faa",
            "template": TPL,
            "name": TPL,
            "description": (
                "ComAp InteliLite NT AMF26P alerts — reads from InfluxDB via HTTP Flux queries.\n"
                "NO direct Modbus polling — Telegraf is the sole Modbus client (IB-Lite is 1-client only).\n"
                "Per-host override: {$INFLUX.HOST} = generator-a or generator-b.\n"
                "Set {$INFLUX.TOKEN} as secret text — mint via:\n"
                "  influx auth create --org cloudxedge --read-bucket 3d6b114d4c2b08c9 --description zabbix-readonly\n"
                "Industry-standard alerts (NFPA 110, ISO 8528-5) with engine_state gating."
            ),
            "groups": [{"name": "Templates/HVAC"}],
            "macros": [
                {"macro": "{$INFLUX.URL}", "value": "http://10.1.250.30:30086", "description": "InfluxDB v2 base URL (NodePort on logmon-k8s)"},
                {"macro": "{$INFLUX.ORG}", "value": "cloudxedge", "description": "InfluxDB organization"},
                {"macro": "{$INFLUX.TOKEN}", "value": "PLACEHOLDER_OVERRIDE_PER_HOST_OR_TEMPLATE", "description": "InfluxDB read-only token (mint with: influx auth create --read-bucket <id>)", "type": "SECRET_TEXT"},
                {"macro": "{$INFLUX.HOST}", "value": "generator-a", "description": "Telegraf host tag for this gen (generator-a / generator-b)"},
                {"macro": "{$GEN.NOMINAL.RPM}", "value": "1500", "description": "Nominal RPM (1500=50Hz, 1800=60Hz)"},
                {"macro": "{$GEN.NOMINAL.V.LN}", "value": "230", "description": "Nominal phase voltage L-N"},
                {"macro": "{$GEN.OVERSPEED.PCT}", "value": "110", "description": "Overspeed threshold (%)"},
                {"macro": "{$GEN.UNDERSPEED.PCT}", "value": "95", "description": "Underspeed under-load threshold (%)"},
                {"macro": "{$BATT.LOW.WARN}", "value": "11.8", "description": "Battery low warning (V) — default for 12V system; override to 23.5 for 24V"},
                {"macro": "{$BATT.LOW.CRIT}", "value": "11.5", "description": "Battery critical (V) — default for 12V; override to 22.5 for 24V"},
                {"macro": "{$BATT.HIGH}", "value": "15.5", "description": "Battery overvoltage (V) — default for 12V; override to 30.0 for 24V"},
                {"macro": "{$OIL.LOW.BAR}", "value": "1.5", "description": "Low oil pressure trip while running (bar)"},
                {"macro": "{$FUEL.LOW.WARN.PCT}", "value": "50", "description": "Fuel level warning (%)"},
                {"macro": "{$FUEL.LOW.CRIT.PCT}", "value": "25", "description": "Fuel level critical NFPA 110 (%)"},
                {"macro": "{$COOLANT.HIGH.C}", "value": "98", "description": "Coolant high temp warn (°C J1939)"},
                {"macro": "{$COOLANT.CRIT.C}", "value": "104", "description": "Coolant shutdown temp (°C J1939)"},
                {"macro": "{$EARTH.FAULT.A}", "value": "5", "description": "Earth fault current threshold (A)"},
                {"macro": "{$SERVICE.LOW.HOURS.WARN}", "value": "50", "description": "Service hours-remaining warn"},
                {"macro": "{$SERVICE.LOW.HOURS.CRIT}", "value": "10", "description": "Service hours-remaining critical"},
            ],
            "items": [build_item(*it) for it in ITEMS],
            "valuemaps": [
                {"uuid": U("vmap-engine"), "name": "ComAp Engine State",
                 "mappings": [{"value": str(v), "newvalue": n} for v, n in ENGINE_STATE_MAP.items()]},
                {"uuid": U("vmap-breaker"), "name": "ComAp Breaker State",
                 "mappings": [{"value": str(v), "newvalue": n} for v, n in BREAKER_STATE_MAP.items()]},
            ],
        }],
        "triggers": [build_trigger(*t) for t in TRIGGERS],
    }
}
print(yaml.safe_dump(template, sort_keys=False, default_flow_style=False, allow_unicode=True))
