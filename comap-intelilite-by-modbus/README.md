# ComAp InteliLite by Modbus (STUB)

Placeholder template. The InteliLite NT generator controller (RO-PLO-S01-Generator-A
@ 10.1.109.53) speaks Modbus TCP via its IB-Lite Ethernet module, but the **register
layout is configuration-specific** — there is no single universal map.

## Blocking item
Need either:
1. **InteliConfig / LiteEdit configuration export** from the gen-set commissioner,
   listing every object's Modbus address as actually programmed; OR
2. A **User-Modbus block** (up to 32 user-defined registers at a fixed range) configured
   on the controller.

## What we know
- IB-Lite web UI: `http://10.1.109.53/sp_index.htm`
- IB-Lite caps at 2 web + 2 Modbus clients simultaneously — Telegraf must remain sole poller
- Slave ID assumed 1, confirm with commissioner

## Until populated
Use `Template Module ICMP Ping` for availability only.

## Generation
Once register list lands, model after `janitza-umg96rm-by-modbus/gen-janitza.py`.
