# NFS Mount Monitoring

Generic template for monitoring NFS mount points on Linux hosts using LLD (`vfs.fs.discovery`).

## Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$NFS_MOUNT_PATH}` | `^/mnt/.*$` | Regex filter for mount path — override per host |
| `{$NFS_FREE_WARN}` | `20` | Warning threshold: free space % |
| `{$NFS_FREE_CRIT}` | `10` | Critical threshold: free space % |

## Discovered items (per NFS mount)
- Free space (bytes and %)
- Used space (bytes)
- Total space (bytes)
- Free inodes (%)

## Triggers
- **High**: free space < `{$NFS_FREE_CRIT}`%
- **Warning**: free space < `{$NFS_FREE_WARN}`%
- **Warning**: free inodes < 20%
- **High**: mount not present or unreachable (no data 15m, manual close)

## Examples

Override `{$NFS_MOUNT_PATH}` at the host level:

| Use case | Value |
|----------|-------|
| Fluentd logging | `^/mnt/nfs/fluentd.*$` |
| OpenStack Glance | `^/mnt/glance.*$` |
| All `/mnt` mounts | `^/mnt/.*$` (default) |
