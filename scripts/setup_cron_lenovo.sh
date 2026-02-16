#!/bin/bash
# Setup Cron Job on Lenovo Tiny for nightly scoring
# Usage: Run this script on Lenovo Tiny directly

echo "⏰ Setting up Cron Job for Nightly Scoring..."

# Create log directory
sudo mkdir -p /opt/zoom-dx/logs
sudo chown -R $(whoami):$(whoami) /opt/zoom-dx/logs

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d) 2>/dev/null || true

# Add new cron job (if not exists)
(crontab -l 2>/dev/null | grep -v "nightly_scoring"; echo "0 3 * * * docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py >> /opt/zoom-dx/logs/scoring.log 2>&1") | crontab -

echo "✅ Cron job configured:"
echo "   - Schedule: Every day at 3:00 AM (JST)"
echo "   - Command: docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py"
echo "   - Log: /opt/zoom-dx/logs/scoring.log"
echo ""

# Display current crontab
echo "📋 Current crontab:"
crontab -l | grep -v "^#"

echo ""
echo "🧪 Test run (dry run):"
echo "   docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py"
