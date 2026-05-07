#!/bin/bash
# /etc/zabbix/scripts/check_proxmox_ddboost_backups.sh

BACKUP_DIR="/mnt/ddboost/dump"

case "$1" in
    "discover")
        # Discover all VMs that have backups
        echo -n '{"data":['
        find "$BACKUP_DIR" -name "vzdump-*.log" -type f | \
        sed -n 's/.*vzdump-\(qemu\|lxc\)-\([0-9]*\)-.*/\2/p' | \
        sort -u | \
        awk '{printf "%s{\"{#VMID}\":\"%s\"}", (NR>1?",":""), $1}'
        echo ']}'
        ;;

    "check_status")
        # Check last backup status for a specific VMID
        VMID=$2
        # Find the most recent log file for this VM
        LATEST_LOG=$(find "$BACKUP_DIR" -name "vzdump-*-${VMID}-*.log" -type f -printf "%T@ %p\n" | sort -rn | head -1 | cut -d' ' -f2-)

        if [ -z "$LATEST_LOG" ]; then
            echo "2"  # No backup found
            exit 0
        fi

        # Check for errors in log
        if grep -q "ERROR:" "$LATEST_LOG"; then
            echo "0"  # Backup failed
        elif grep -q "INFO: Finished Backup of VM" "$LATEST_LOG" || grep -q "INFO: archive file size:" "$LATEST_LOG"; then
            echo "1"  # Backup successful
        else
            echo "2"  # Unknown status
        fi
        ;;

    "last_backup_time")
        # Get timestamp of last backup for a VM
        VMID=$2
        find "$BACKUP_DIR" -name "vzdump-*-${VMID}-*.log" -type f -printf "%T@\n" | sort -rn | head -1 | cut -d. -f1
        ;;

    "backup_age_hours")
        # Calculate age in hours since last backup
        VMID=$2
        LAST_BACKUP=$(find "$BACKUP_DIR" -name "vzdump-*-${VMID}-*.log" -type f -printf "%T@\n" | sort -rn | head -1)
        if [ -z "$LAST_BACKUP" ]; then
            echo "999999"  # No backup found
        else
            NOW=$(date +%s)
            AGE=$((($NOW - ${LAST_BACKUP%.*}) / 3600))
            echo "$AGE"
        fi
        ;;

    "backup_size")
        # Get size of last backup in MB
        VMID=$2
        find "$BACKUP_DIR" -name "vzdump-*-${VMID}-*.vma.zst" -type f -printf "%T@ %s\n" | sort -rn | head -1 | awk '{print int($2/1024/1024)}'
        ;;

    "total_backups")
        # Count total number of backup files
        find "$BACKUP_DIR" -name "vzdump-*.vma.zst" -type f | wc -l
        ;;

    "failed_today")
        # Count failed backups in last 24h
        find "$BACKUP_DIR" -name "vzdump-*.log" -type f -mtime -1 -exec grep -l "ERROR:" {} \; | wc -l
        ;;

    "storage_usage_percent")
        # Get storage usage percentage
        df /mnt/ddboost | awk 'NR==2 {print $5}' | sed 's/%//'
        ;;

    "storage_free_gb")
        # Get free space in GB
        df -BG /mnt/ddboost | awk 'NR==2 {print $4}' | sed 's/G//'
        ;;

    *)
        echo "Usage: $0 {discover|check_status|last_backup_time|backup_age_hours|backup_size|total_backups|failed_today|storage_usage_percent|storage_free_gb} [VMID]"
        exit 1
        ;;
esac
