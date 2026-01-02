# Wazuh Automation Lab 🛡️

A collection of scripts to automate monitoring and reporting for Wazuh SIEM in a Docker environment. This repository accompanies my Medium articles on building a SOC Lab.

## 📂 Contents

1. **[wazuh-report.sh](wazuh-report.sh)** - Automates PDF report generation from Wazuh Dashboard and sends it via Gmail using SMTP.
2. **[wazuh_to_sheets.py](wazuh_to_sheets.py)** - Syncs Wazuh Agents inventory directly to Google Sheets using Python and Google Cloud API.

---

## 🚀 1. Automated PDF Reporting (Bash)

This script uses `opensearch-reporting-cli` to bypass SSL errors in a local lab environment (Docker) and deliver reports via SMTP.

### Prerequisites

* Wazuh Dashboard running on Docker.
* **Node.js** installed.
* `opensearch-reporting-cli` installed:
```bash
  npm install -g @opensearch-project/reporting-cli
```
* Gmail Account with App Password generated (if using Gmail).

### Usage

1. Edit `wazuh-report.sh` and set your credentials (URL, Auth, SMTP).
2. Make the script executable:
```bash
   chmod +x wazuh-report.sh
```
3. Run manually:
```bash
   ./wazuh-report.sh
```
4. (Optional) Set up a Cronjob for daily reports at 8 AM:
```bash
   0 8 * * * /path/to/wazuh-report.sh >> /var/log/wazuh-report.log 2>&1
```

---

## 📊 2. Live Inventory to Google Sheets (Python)

This script fetches active agents from the Wazuh API and updates a specific Google Sheet in real-time using a Service Account.

### Prerequisites

* Python 3.x
* Google Cloud Service Account (JSON Key).
* Google Sheets API & Drive API enabled in GCP Console.

### Installation

1. Install required Python libraries:
```bash
   pip install -r requirements.txt
```
   (Content of `requirements.txt`: `requests`, `google-api-python-client`, `google-auth`)

2. **Credentials Setup:**
   * Place your GCP `credentials.json` in the same folder as the script.
   * **Important:** Share your Google Sheet with the Service Account email address (give Editor access).

3. **Configuration:**
   * Open `wazuh_to_sheets.py`.
   * Update `WAZUH_HOST`, `WAZUH_USER`, `WAZUH_PASSWORD`, and `SPREADSHEET_ID`.

### Usage

Run the script:
```bash
python3 wazuh_to_sheets.py
```

---

## 📝 Read the Articles

* Part 1: How I Automated Wazuh PDF Reporting (Add your Medium link here)
* Part 2: Real-time Server Inventory with Python & Google Sheets (Add your Medium link here)

---

## ⚠️ Disclaimer

These scripts are intended for **Lab/Testing environments**. For production use, please implement robust secrets management (e.g., Environment Variables, Vault, or Docker Secrets) instead of hardcoding credentials.
