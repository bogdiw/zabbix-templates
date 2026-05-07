# Emergency Dashboard

Zabbix dashboard backup for the Platform & Infrastructure emergency view.

## Widgets
- Platform Public Services (trigger overview)
- Platform Services Internal (trigger overview)
- BGP Sessions (honeycomb)
- RTR01/RTR02 Interfaces (honeycomb)
- OpenStack Control Plane VMs (trigger overview)
- Platform & Infrastructure Problems
- OpenStack API Services — Kolla (trigger overview)
- Host Availability
- High & Disaster Problems
- OpenStack Nova — Service Health / Problems

## Restore
Import via Zabbix API:
```bash
curl -sk -X POST "https://zabbix.infra.cloudxedge.com/api_jsonrpc.php" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"jsonrpc":"2.0","method":"dashboard.update","params":<dashboard-json>,"id":1}'
```
