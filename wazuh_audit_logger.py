#!/usr/bin/env python3
"""
Wazuh Critical Alert Logger to Google Sheets
Automatically fetches critical security alerts from Wazuh Indexer (OpenSearch)
and logs them to a Google Spreadsheet for audit trail purposes.
"""

import json
import requests
import urllib3
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= CONFIGURATION =================
# 1. Wazuh Indexer (OpenSearch) Settings
INDEXER_HOST = 'https://localhost:9200'  # Replace with your Wazuh Indexer host
INDEXER_USER = 'admin'  # Replace with your username
INDEXER_PASS = 'YOUR_WAZUH_PASSWORD'  # Replace with your Wazuh Dashboard password

# 2. Google Sheets Configuration
SERVICE_ACCOUNT_FILE = '/path/to/your/credentials.json'  # Path to Google Service Account credentials
SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'  # Your Google Spreadsheet ID
RANGE_NAME = 'Sheet1!A1'  # Sheet name and starting cell (adjust if needed)

# 3. Alert Filtering Options
MIN_LEVEL = 10  # Only log alerts with level >= 10 (Critical alerts)
TIME_WINDOW_MINUTES = 60  # Fetch alerts from last 60 minutes (adjust based on your cron schedule)

# ================= MAIN LOGIC =================

def get_critical_alerts():
    """
    Fetch critical alerts from Wazuh Indexer based on configured filters.
    
    Returns:
        list: Parsed alert data ready for Google Sheets insertion
    """
    print(f"[1/3] Fetching alerts with Level >= {MIN_LEVEL} from last {TIME_WINDOW_MINUTES} minutes...")
    
    # Use timezone-aware datetime to avoid deprecation warnings
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=TIME_WINDOW_MINUTES)
    
    # OpenSearch Query DSL (Database Query Language)
    query = {
        "size": 100,  # Maximum 100 alerts per execution (prevents spam)
        "query": {
            "bool": {
                "must": [
                    {"range": {"rule.level": {"gte": MIN_LEVEL}}},  # Filter by alert level
                    {"range": {"@timestamp": {"gte": past.isoformat()}}}  # Filter by time range
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "asc"}}]  # Sort from oldest to newest
    }

    url = f"{INDEXER_HOST}/wazuh-alerts-*/_search"
    auth = (INDEXER_USER, INDEXER_PASS)
    headers = {'Content-Type': 'application/json'}

    try:
        # Add timeout to prevent script from hanging indefinitely
        response = requests.get(url, auth=auth, json=query, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        hits = response.json()['hits']['hits']
        print(f"      Found {len(hits)} critical alerts.")
        
        parsed_alerts = []
        for item in hits:
            source = item['_source']
            
            # Extract 'data' object from alert
            data_obj = source.get('data', {})

            # --- IP ADDRESS DETECTION LOGIC (FINAL VERSION) ---
            # Priority 1: Check standard Wazuh field (srcip)
            attacker_ip = data_obj.get('srcip')
            
            # Priority 2: Check 'remote_addr' directly in 'data' object
            if not attacker_ip:
                attacker_ip = data_obj.get('remote_addr')
                
            # Priority 3: Check 'client_ip' directly in 'data' object (fallback)
            if not attacker_ip:
                attacker_ip = data_obj.get('client_ip')
                
            # Default: If all fields are empty, use dash
            if not attacker_ip:
                attacker_ip = "-"
            # --------------------------------------------------

            # Format row for Spreadsheet insertion
            row = [
                source.get('@timestamp', '-'),
                source.get('rule', {}).get('level', '-'),
                source.get('rule', {}).get('id', '-'),
                source.get('rule', {}).get('description', '-'),
                source.get('agent', {}).get('name', 'Server'),
                attacker_ip  # Using the detected IP address
            ]
            parsed_alerts.append(row)
            
        return parsed_alerts

    except Exception as e:
        print(f"[ERROR] Failed to connect to OpenSearch: {e}")
        return []

def append_to_sheet(rows):
    """
    Append alert data to Google Sheets.
    
    Args:
        rows (list): List of alert rows to append
    """
    if not rows:
        print("[INFO] No new data to write.")
        return

    print(f"[2/3] Appending {len(rows)} rows to Audit Log...")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    body = {'values': rows}
    
    # KEY POINT: Use append() method, not update()
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, 
        range=RANGE_NAME,
        valueInputOption='RAW', 
        insertDataOption='INSERT_ROWS',  # Insert new rows, don't overwrite
        body=body
    ).execute()
    
    print("[3/3] Successfully logged to Audit Log.")

if __name__ == '__main__':
    alerts = get_critical_alerts()
    append_to_sheet(alerts)
