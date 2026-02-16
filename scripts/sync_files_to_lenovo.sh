#!/bin/bash
# ========================================
# Transfer Updated Files to Lenovo Tiny
# ========================================
# Run this on Mac to copy fixed files to Lenovo Tiny

set -e

LENOVO_IP="100.107.246.40"
LENOVO_USER="onodera"
REMOTE_DIR="C:/Users/onodera/zoom-dx"

echo "📦 Transferring updated files to Lenovo Tiny..."
echo "Target: $LENOVO_USER@$LENOVO_IP"
echo "========================================"
echo ""

# Check connection
echo -n "1. Checking Tailscale connection... "
if ping -c 1 -W 1 $LENOVO_IP > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Failed"
    echo "   Please ensure Tailscale is running"
    exit 1
fi

# Create temp directory for transfer
TEMP_DIR="/tmp/zoom-dx-update-$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "2. Preparing files for transfer..."

# Copy only the essential updated files
cp backend/config.py "$TEMP_DIR/"
cp docker-compose.lenovo.yml "$TEMP_DIR/"
cp scripts/update_lenovo_local.ps1 "$TEMP_DIR/"

# Create archive
cd "$TEMP_DIR"
tar -czf update.tar.gz *

echo "   ✅ Archive created"

# Transfer archive
echo "3. Transferring files..."
echo "   (Password: Zoom5145)"

# Use scp with password (requires sshpass or manual password entry)
if command -v sshpass &> /dev/null; then
    sshpass -p "Zoom5145" scp "$TEMP_DIR/update.tar.gz" "$LENOVO_USER@$LENOVO_IP:C:/Users/onodera/update.tar.gz"
else
    echo "   Please enter password: Zoom5145"
    scp "$TEMP_DIR/update.tar.gz" "$LENOVO_USER@$LENOVO_IP:C:/Users/onodera/update.tar.gz"
fi

echo "   ✅ Files transferred"

# Extract on remote side
echo "4. Extracting files on Lenovo Tiny..."
ssh "$LENOVO_USER@$LENOVO_IP" "powershell -Command \"
    cd C:/Users/onodera/zoom-dx;
    tar -xzf C:/Users/onodera/update.tar.gz -C .;
    Remove-Item C:/Users/onodera/update.tar.gz;
    Write-Host 'Files extracted successfully';
\""

echo "   ✅ Extraction complete"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "✅ File Transfer Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. RDP or SSH to Lenovo Tiny"
echo "   2. Open PowerShell as Administrator"
echo "   3. Run: cd C:\\Users\\onodera\\zoom-dx"
echo "   4. Run: .\\scripts\\update_lenovo_local.ps1"
echo ""
echo "OR run remotely from here:"
echo "   ssh $LENOVO_USER@$LENOVO_IP \"powershell -ExecutionPolicy Bypass -File C:/Users/onodera/zoom-dx/scripts/update_lenovo_local.ps1\""
echo ""
