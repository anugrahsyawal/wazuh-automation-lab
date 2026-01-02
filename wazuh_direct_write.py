#!/usr/bin/env python3
import json
import requests
import urllib3
from base64 import b64encode
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ====================================================================
# CONFIGURATION (UPDATE THIS SECTION)
# ====================================================================

# 1. Wazuh API Credentials
WAZUH_HOST = 'YOUR_WAZUH_MANAGER_IP'  # e.g., localhost or 192.168.x.x
WAZUH_PORT = 55000
WAZUH_USER = 'YOUR_WAZUH_USERNAME'    # e.g., wazuh-wui
WAZUH_PASSWORD = 'YOUR_WAZUH_PASSWORD'

# 2. Google Cloud & Sheets Configuration
# Path to your Google Service Account JSON file
SERVICE_ACCOUNT_FILE = './credentials.json'

# The ID of the Google Sheet (Found in the URL of your spreadsheet)
# Example: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
SPREADSHEET_ID = 'YOUR_GOOGLE_SPREADSHEET_ID'

# The Tab/Sheet name in your Google Spreadsheet
RANGE_NAME = 'Sheet1!A1'

# ====================================================================
# PROGRAM LOGIC
# ====================================================================

def get_wazuh_agents():
    print("[1/3] Fetching data from Wazuh API...")
    login_url = f"https://{WAZUH_HOST}:{WAZUH_PORT}/security/user/authenticate"
    basic_auth = f"{WAZUH_USER}:{WAZUH_PASSWORD}".encode()
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Basic {b64encode(basic_auth).decode()}'}
    
    # Login to retrieve Token
    try:
        response = requests.post(login_url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        token = response.json()['data']['token']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Login failed: {e}")
    
    # Get Agents Data
    agents_url = f"https://{WAZUH_HOST}:{WAZUH_PORT}/agents?limit=1000" # Added limit just in case
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(agents_url, headers=headers, verify=False)
    response.raise_for_status()
    
    agents_data = response.json()['data']['affected_items']
    
    # Format Data for Google Sheets (List of Lists)
    # Header Row
    values = [['Agent ID', 'Hostname', 'IP Address', 'OS Name', 'OS Version', 'Status', 'Last Keep Alive', 'Wazuh Version']]
    
    # Data Rows
    for agent in agents_data:
        # safely get values using .get() to avoid errors on missing keys
        row = [
            str(agent.get('id', '-')),
            str(agent.get('name', '-')),
            str(agent.get('ip', '-')),
            str(agent.get('os', {}).get('name', '-')),
            str(agent.get('os', {}).get('version', '-')),
            str(agent.get('status', '-')),
            str(agent.get('lastKeepAlive', '-')),
            str(agent.get('version', '-'))
        ]
        values.append(row)
        
    return values

def update_google_sheet(values):
    print("[2/3] Connecting to Google Sheets...")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        # 1. Clear old data first
        print("      Clearing old data...")
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1'
        ).execute()

        # 2. Write new data
        print(f"[3/3] Writing {len(values)} rows to Google Sheet...")
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='RAW', body=body
        ).execute()

        print(f"      SUCCESS! {result.get('updatedCells')} cells updated.")
        
    except FileNotFoundError:
        raise Exception(f"Credentials file not found at: {SERVICE_ACCOUNT_FILE}")
    except Exception as e:
        raise Exception(f"Google Sheets Error: {e}")

# MAIN EXECUTION
if __name__ == '__main__':
    try:
        data_rows = get_wazuh_agents()
        update_google_sheet(data_rows)
        print("\n[DONE] Check your Google Sheet now.")
    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
