# Backup & Restore Runbook

## Overview
This runbook documents the backup and restore procedures for the HUUGIAU Fashion Website.

## Backup Strategy

### Backup Schedule
| Backup Type | Frequency | Retention | Storage |
|-------------|-----------|-----------|---------|
| Database | Hourly (continuous via WAL) + Daily full | 30 days | Local + S3 |
| Media Files | Daily | 30 days | Local + S3 |
| Configuration | On change | 90 days | Git + S3 |

### Backup Types

#### 1. Database Backup
- **PostgreSQL**: `pg_dump` with custom format + compression
- **SQL Server**: `sqlcmd` BACKUP DATABASE with compression
- Frequency: Continuous (WAL archiving) + Daily full
- Retention: 30 days local, 90 days S3

#### 2. Media Files Backup
- User uploads, product images, static assets
- Frequency: Daily
- Format: tar.gz with compression
- Retention: 30 days local, 90 days S3

#### 3. Configuration Backup
- Git repository (code + config)
- Environment variables (encrypted)
- Docker configs
- Retention: 90 days

---

## Backup Procedures

### Automated Daily Backup (Cron)
```bash
# Add to crontab
0 2 * * * /app/scripts/backup.sh full >> /var/log/backup.log 2>&1
```

### Manual Backup
```bash
# Full backup
./scripts/backup.sh full

# Database only
./scripts/backup.sh db

# Media only
./scripts/backup.sh media
```

### S3 Upload
Set environment variables:
```bash
export BACKUP_S3_BUCKET=your-bucket-name
export AWS_REGION=ap-southeast-1
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
```

---

## Restore Procedures

### Database Restore
```bash
# List available backups
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh db /backups/db/fashion-website_db_20240115_020000.sql.gz

# Or for SQL Server
./scripts/restore.sh db /backups/db/fashion-website_db_20240115_020000.sql.gz
```

### Media Restore
```bash
# List available backups
./scripts/restore.sh media

# Restore specific media backup
./scripts/restore.sh media /backups/media/fashion-website_media_20240115_020000.tar.gz
```

### Full Disaster Recovery
```bash
# 1. Provision new server
# 2. Install dependencies (Docker, Docker Compose)
# 3. Clone repository
# 4. Restore database
./scripts/restore.sh db /backups/db/latest.sql.gz

# 5. Restore media
./scripts/restore.sh media /backups/media/latest.tar.gz

# 6. Start services
docker-compose up -d

# 7. Run migrations
docker-compose exec backend python manage.py migrate

# 7. Verify health
curl -f http://localhost:8000/api/health/ready/
```

---

## Recovery Time Objectives (RTO/RPO)

| Component | RTO | RPO |
|-----------|-----|-----|
| Database | 30 min | 1 hour |
| Media Files | 1 hour | 24 hours |
| Full System | 2 hours | 1 hour |

---

## Monitoring & Alerts

### Backup Monitoring
- **Success**: Daily log check via cron email
- **Failure**: Alert via email/Slack within 15 min
- **Verification**: Weekly test restore (automated)

### Alert Rules
```yaml
# Prometheus alert rules
- alert: BackupFailed
  expr: increase(backup_job_failed_total[1h]) > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Backup job failed"
    
- alert: BackupStale
  expr: time() - backup_last_success_timestamp > 86400
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Backup older than 24 hours"
```

---

## Disaster Recovery Checklist

### Pre-Disaster
- [ ] Backup scripts tested monthly
- [ ] Restore procedures documented and tested quarterly
- [ ] S3 bucket versioning enabled
- [ ] Cross-region replication configured
- [ ] Encryption keys backed up securely

### During Incident
1. **Assess impact** - Determine scope (DB only, media only, full)
2. **Communicate** - Notify stakeholders
3. **Execute restore** - Follow restore procedures
4. **Verify** - Run health checks
5. **Communicate** - All clear to stakeholders

### Post-Incident
- [ ] Root cause analysis
- [ ] Update runbook if needed
- [ ] Update monitoring/alerts
- [ ] Schedule follow-up test

---

## Contact Information

| Role | Contact | Escalation |
|------|---------|------------|
| Primary DBA | dba@huugiau.local | +84-xxx-xxx-xxx |
| DevOps Lead | devops@huugiau.local | +84-xxx-xxx-xxx |
| CTO | cto@huugiau.local | +84-xxx-xxx-xxx |

---

## Testing Schedule

| Test | Frequency | Responsible |
|------|-----------|-------------|
| Full DB restore | Monthly | DBA |
| Media restore | Quarterly | DevOps |
| Full DR drill | Semi-annually | Team |
| Backup monitoring | Daily | Monitoring |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | DevOps Team | Initial version |
| 1.1 | 2024-03-01 | DevOps Team | Added SQL Server support |