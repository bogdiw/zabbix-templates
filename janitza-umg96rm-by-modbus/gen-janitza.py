#!/usr/bin/env python3
"""Zabbix 7.2 template for Janitza UMG96RM-E via Modbus TCP (agent2 modbus plugin)."""
import uuid, yaml

NS = uuid.UUID("a1b2c3d4-0000-0000-0000-000000000002")
def U(key):
    u = uuid.uuid5(NS, key)
    b = bytearray(u.bytes)
    b[6] = (b[6] & 0x0F) | 0x40
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b)).hex

# (key_suffix, name, register_addr, units)
REGS = [
    ("voltage_l1n",            "Voltage L1-N",         19000, "V"),
    ("voltage_l2n",            "Voltage L2-N",         19002, "V"),
    ("voltage_l3n",            "Voltage L3-N",         19004, "V"),
    ("voltage_l1l2",           "Voltage L1-L2",        19006, "V"),
    ("voltage_l2l3",           "Voltage L2-L3",        19008, "V"),
    ("voltage_l3l1",           "Voltage L3-L1",        19010, "V"),
    ("current_l1",             "Current L1",           19012, "A"),
    ("current_l2",             "Current L2",           19014, "A"),
    ("current_l3",             "Current L3",           19016, "A"),
    ("current_vector_sum",     "Current vector sum",   19018, "A"),
    ("active_power_l1",        "Active power L1",      19020, "W"),
    ("active_power_l2",        "Active power L2",      19022, "W"),
    ("active_power_l3",        "Active power L3",      19024, "W"),
    ("active_power_total",     "Active power total",   19026, "W"),
    ("apparent_power_l1",      "Apparent power L1",    19028, "VA"),
    ("apparent_power_l2",      "Apparent power L2",    19030, "VA"),
    ("apparent_power_l3",      "Apparent power L3",    19032, "VA"),
    ("apparent_power_total",   "Apparent power total", 19034, "VA"),
    ("reactive_power_l1",      "Reactive power L1",    19036, "var"),
    ("reactive_power_l2",      "Reactive power L2",    19038, "var"),
    ("reactive_power_l3",      "Reactive power L3",    19040, "var"),
    ("reactive_power_total",   "Reactive power total", 19042, "var"),
    ("cosphi_l1",              "Cos phi L1",           19044, ""),
    ("cosphi_l2",              "Cos phi L2",           19046, ""),
    ("cosphi_l3",              "Cos phi L3",           19048, ""),
    ("frequency",              "Frequency",            19050, "Hz"),
    ("rotation_field",         "Rotation field",       19052, ""),
    ("energy_active_l1",       "Energy active L1",       19054, "Wh"),
    ("energy_active_l2",       "Energy active L2",       19056, "Wh"),
    ("energy_active_l3",       "Energy active L3",       19058, "Wh"),
    ("energy_active_total",    "Energy active total",    19060, "Wh"),
    ("energy_active_imp_l1",   "Energy active import L1",19062, "Wh"),
    ("energy_active_imp_l2",   "Energy active import L2",19064, "Wh"),
    ("energy_active_imp_l3",   "Energy active import L3",19066, "Wh"),
    ("energy_active_imp_total","Energy active import total",19068,"Wh"),
    ("energy_active_exp_l1",   "Energy active export L1",19070, "Wh"),
    ("energy_active_exp_l2",   "Energy active export L2",19072, "Wh"),
    ("energy_active_exp_l3",   "Energy active export L3",19074, "Wh"),
    ("energy_active_exp_total","Energy active export total",19076,"Wh"),
    ("energy_apparent_l1",     "Energy apparent L1",     19078, "VAh"),
    ("energy_apparent_l2",     "Energy apparent L2",     19080, "VAh"),
    ("energy_apparent_l3",     "Energy apparent L3",     19082, "VAh"),
    ("energy_apparent_total",  "Energy apparent total",  19084, "VAh"),
    ("energy_reactive_l1",     "Energy reactive L1",     19086, "varh"),
    ("energy_reactive_l2",     "Energy reactive L2",     19088, "varh"),
    ("energy_reactive_l3",     "Energy reactive L3",     19090, "varh"),
    ("energy_reactive_total",  "Energy reactive total",  19092, "varh"),
    ("energy_reactive_ind_l1", "Energy reactive ind L1", 19094, "varh"),
    ("energy_reactive_ind_l2", "Energy reactive ind L2", 19096, "varh"),
    ("energy_reactive_ind_l3", "Energy reactive ind L3", 19098, "varh"),
    ("energy_reactive_ind_total","Energy reactive ind total",19100,"varh"),
    ("energy_reactive_cap_l1", "Energy reactive cap L1", 19102, "varh"),
    ("energy_reactive_cap_l2", "Energy reactive cap L2", 19104, "varh"),
    ("energy_reactive_cap_l3", "Energy reactive cap L3", 19106, "varh"),
    ("energy_reactive_cap_total","Energy reactive cap total",19108,"varh"),
    ("thd_voltage_l1",         "THD voltage L1",         19110, "%"),
    ("thd_voltage_l2",         "THD voltage L2",         19112, "%"),
    ("thd_voltage_l3",         "THD voltage L3",         19114, "%"),
    ("thd_current_l1",         "THD current L1",         19118, "%"),
    ("thd_current_l2",         "THD current L2",         19120, "%"),
    ("thd_current_l3",         "THD current L3",         19122, "%"),
]

TPL = "Janitza UMG96RM-E by Modbus"

# Trigger reference keys (full modbus.get keys must match item keys exactly)
def mkkey(addr): return f'modbus.get[{{$MODBUS.HOST}},{{$MODBUS.SLAVE}},3,{addr},1,float,be]'
FREQ_KEY = mkkey(19050)
V_L1N_KEY = mkkey(19000)
TRIGGERS = [
    ("freq_low",   f"last(/{{T}}/{FREQ_KEY})<49.5 and last(/{{T}}/{FREQ_KEY})>0",
        "Janitza meter frequency below 49.5 Hz on {HOST.NAME}", "WARNING"),
    ("freq_high",  f"last(/{{T}}/{FREQ_KEY})>50.5",
        "Janitza meter frequency above 50.5 Hz on {HOST.NAME}", "WARNING"),
    ("voltage_low",f"last(/{{T}}/{V_L1N_KEY})<200 and last(/{{T}}/{V_L1N_KEY})>0",
        "Janitza L1-N voltage below 200 V on {HOST.NAME}", "WARNING"),
    ("no_data",    f"nodata(/{{T}}/{FREQ_KEY},5m)=1",
        "Janitza meter not reporting on {HOST.NAME}", "AVERAGE"),
]

def build():
    items = []
    for suffix, name, addr, units in REGS:
        key = f"meter.{suffix}"
        item = {
            "uuid": U(f"item:{key}"),
            "name": f"Meter: {name}",
            "type": "ZABBIX_ACTIVE",
            # Zabbix agent2 modbus.get key:
            # modbus.get[<endpoint>, <slave>, <function>, <address>, <count>, <type>, <endianness>, <offset>]
            "key": f'modbus.get[{{$MODBUS.HOST}},{{$MODBUS.SLAVE}},3,{addr},1,float,be]',
            "delay": "1m",
            "history": "31d",
            "trends": "365d",
            "value_type": "FLOAT",
            "preprocessing": [
                {"type":"JSONPATH", "parameters": ["$[0]"]},
            ],
            "tags": [{"tag":"class","value":"meter"},{"tag":"vendor","value":"janitza"}],
        }
        if units: item["units"] = units
        items.append(item)

    triggers = [{
        "uuid": U(f"trig:{k}"),
        "expression": expr.replace("{T}", TPL),
        "name": descr,
        "priority": sev,
    } for k, expr, descr, sev in TRIGGERS]

    tpl = {
        "zabbix_export": {
            "version": "7.2",
            "template_groups": [{"uuid": U("tg:hvac"), "name": "Templates/HVAC"}],
            "templates": [{
                "uuid": U("tpl:janitza-umg96"),
                "template": TPL,
                "name": TPL,
                "description": "Janitza UMG96RM-E power meter via Modbus TCP. 61 holding registers (FLOAT32 ABCD, big-endian) starting at 19000. Requires Zabbix agent 2 with modbus plugin reachable from the Zabbix server. Set {$MODBUS.HOST} = tcp://<meter-ip>:502 and {$MODBUS.SLAVE} per host.",
                "groups": [{"name": "Templates/HVAC"}],
                "items": items,
                "macros": [
                    {"macro":"{$MODBUS.HOST}","value":"tcp://10.1.109.55:502","description":"Modbus TCP endpoint URL"},
                    {"macro":"{$MODBUS.SLAVE}","value":"1","description":"Modbus slave/unit ID"},
                ],
            }],
            "triggers": triggers,
        }
    }
    return tpl

if __name__ == "__main__":
    print(yaml.dump(build(), sort_keys=False, default_flow_style=False, width=120))
