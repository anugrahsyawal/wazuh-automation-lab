#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# WAZUH AUTOMATED REPORTING SCRIPT
# Description: Generates and emails Wazuh dashboard snapshots using SMTP.
# ==========================================

# --- CONFIGURATION ---

# 1. Snapshot URL
# Ensure this is a valid Short URL from the OpenSearch/Wazuh Dashboard.
URL="https://YOUR_WAZUH_DOMAIN/goto/YOUR_SNAPSHOT_ID"

# 2. Wazuh Credentials (To access the dashboard data)
AUTH_TYPE="basic"
# Format: username:password
CREDS="admin:YOUR_WAZUH_PASSWORD"

# 3. SMTP Configuration (Example: Gmail)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="465"
SMTP_USER="your_email@gmail.com"
# Use App Password if using Gmail (Not your login password)
SMTP_PASS="your_16_digit_app_password"

# 4. Email Sender & Recipient
FROM="your_email@gmail.com"
TO="recipient_email@example.com"

# 5. Report Metadata
FORMAT="pdf"
SUBJECT="[Wazuh] Daily Security Report"
NOTE=$'Hello,\n\nPlease find attached the daily security report generated from the Wazuh Dashboard.\n\nRegards,\nSOC Automation'

# ----- Environment Setup -----
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export NODE_TLS_REJECT_UNAUTHORIZED=0 # Bypass SSL for Self-Signed Certs

# Check for Reporting CLI
CLI="$(command -v opensearch-reporting-cli || true)"
if [[ -z "$CLI" ]]; then
    echo "ERROR: opensearch-reporting-cli not found."
    echo "Please install it using: npm i -g @opensearch-project/reporting-cli"
    exit 1
fi

echo "[*] Starting report generation..."
echo "[*] Target URL: $URL"
echo "[*] Sending via: $SMTP_HOST ($SMTP_USER)"

# ----- EXECUTION -----
"$CLI" \
 -u "$URL" \
 -a "$AUTH_TYPE" -c "$CREDS" \
 -e smtp \
 --smtphost "$SMTP_HOST" \
 --smtpport "$SMTP_PORT" \
 --smtpusername "$SMTP_USER" \
 --smtppassword "$SMTP_PASS" \
 --smtpsecure true \
 --selfsignedcerts true \
 -s "$FROM" -r "$TO" \
 -f "$FORMAT" \
 --subject "$SUBJECT" \
 --note "$NOTE"

echo "[*] Done! Please check the recipient's inbox."
