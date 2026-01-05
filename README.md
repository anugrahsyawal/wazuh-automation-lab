# Wazuh Critical Alert Logger to Google Sheets

Automatically fetch critical security alerts from Wazuh Indexer and log them to Google Sheets for audit trail purposes.

![Project Banner](./images/banner.png)
<!-- Replace with your project banner/logo -->

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Results](#results)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

This project provides an automated solution for monitoring and logging critical security alerts from Wazuh SIEM to Google Sheets. It queries the Wazuh Indexer (OpenSearch) for high-severity alerts and maintains an audit trail in a centralized spreadsheet.

**Use Cases:**
- Security audit trail maintenance
- Compliance reporting
- Real-time security monitoring
- Incident response documentation
- Collaborative security analysis

## 🏗️ Architecture

![Architecture Diagram](./images/architecture.png)
<!-- Add your system architecture diagram here -->

**System Flow:**
1. Script queries Wazuh Indexer via REST API
2. Filters alerts based on severity level and time window
3. Extracts relevant security information
4. Appends formatted data to Google Sheets
5. Can be scheduled via cron for automated execution

**Components:**
- **Wazuh Indexer (OpenSearch)**: Source of security alerts
- **Python Script**: Data extraction and transformation
- **Google Sheets API**: Data storage and visualization
- **Cron Scheduler**: Automated execution (optional)

## ✨ Features

- ✅ Fetches alerts with configurable severity level (default: Level ≥ 10)
- ✅ Automatically extracts attacker IP from multiple field variations
- ✅ Logs to Google Sheets with timestamp, severity, rule ID, and description
- ✅ Timezone-aware datetime handling
- ✅ Configurable time window for alert retrieval
- ✅ Error handling and connection timeout protection
- ✅ Support for self-signed SSL certificates
- ✅ Prevents duplicate logging with smart time windows

## 📦 Prerequisites

- **Python 3.7+**
- **Wazuh Indexer (OpenSearch)** with API access
- **Google Service Account** with Sheets API enabled
- **Google Spreadsheet** with appropriate sharing permissions

### Required Python Libraries
```bash
requests
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
urllib3
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/wazuh-alert-logger.git
cd wazuh-alert-logger
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client urllib3
```

### 3. Set Up Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API**
4. Create a **Service Account**
5. Download the credentials JSON file
6. Save it as `credentials.json` in your project directory

![Google Service Account Setup](./images/google-service-account.png)
<!-- Add screenshot of Google Service Account creation -->

### 4. Configure Google Sheets

1. Create a new Google Spreadsheet
2. Share it with your Service Account email (found in credentials.json)
3. Give **Editor** permissions
4. Copy the Spreadsheet ID from the URL

**Example Spreadsheet URL:**
```
https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
```

![Google Sheets Setup](./images/sheets-setup.png)
<!-- Add screenshot of Google Sheets with sample data -->

## ⚙️ Configuration

Edit the `wazuh_audit_logger.py` file:

```python
# Wazuh Indexer Configuration
INDEXER_HOST = 'https://your-wazuh-host:9200'  # Your Wazuh Indexer host
INDEXER_USER = 'admin'                          # Username
INDEXER_PASS = 'your_password'                  # Password

# Google Sheets Configuration
SERVICE_ACCOUNT_FILE = '/path/to/credentials.json'  # Path to credentials
SPREADSHEET_ID = 'your_spreadsheet_id'              # Your Spreadsheet ID
RANGE_NAME = 'Sheet1!A1'                            # Sheet name and range

# Alert Filtering
MIN_LEVEL = 10              # Minimum alert severity (10 = Critical)
TIME_WINDOW_MINUTES = 60    # Time range to fetch alerts
```

### Configuration Options

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `MIN_LEVEL` | Minimum alert severity level | 10 | 1-15 (Wazuh levels) |
| `TIME_WINDOW_MINUTES` | Time range to fetch alerts | 60 | Any positive integer |
| `RANGE_NAME` | Google Sheets starting cell | Sheet1!A1 | Any valid range |
| `query["size"]` | Maximum alerts per execution | 100 | 1-10000 |

## 🎯 Usage

### Manual Execution

Run the script manually:
```bash
python3 wazuh_audit_logger.py
```

**Expected Output:**
```
[1/3] Fetching alerts with Level >= 10 from last 60 minutes...
      Found 5 critical alerts.
[2/3] Appending 5 rows to Audit Log...
[3/3] Successfully logged to Audit Log.
```

### Automated Execution with Cron

For hourly execution:
```bash
crontab -e
```

Add this line:
```bash
0 * * * * /usr/bin/python3 /path/to/wazuh_audit_logger.py >> /var/log/wazuh_logger.log 2>&1
```

**Common Cron Schedules:**
- Every hour: `0 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every 15 minutes: `*/15 * * * *`
- Daily at 9 AM: `0 9 * * *`

### Spreadsheet Output Format

The script appends data with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | Alert generation time | 2026-01-05T10:30:45.123Z |
| Level | Alert severity level | 10 |
| Rule ID | Wazuh rule identifier | 5710 |
| Description | Alert description | Multiple authentication failures |
| Agent Name | Source agent/server | web-server-01 |
| Attacker IP | Source IP address | 192.168.1.100 |

## 📊 Results

### Sample Output

![Sample Google Sheets Output](./images/sample-output.png)
<!-- Add screenshot of Google Sheets with logged alerts -->

### Dashboard View

![Dashboard Visualization](./images/dashboard.png)
<!-- Add screenshot of any dashboard or chart you create from the data -->

### Alert Statistics

![Alert Statistics](./images/statistics.png)
<!-- Add screenshot showing alert trends, pie charts, or other visualizations -->

## 🔧 Troubleshooting

### Connection Error to Wazuh Indexer

**Symptoms:**
```
[ERROR] Failed to connect to OpenSearch: Connection refused
```

**Solutions:**
- Verify Wazuh Indexer credentials (`INDEXER_USER` and `INDEXER_PASS`)
- Check network connectivity: `curl -k https://your-wazuh-host:9200`
- Ensure port 9200 is accessible and not blocked by firewall
- Verify SSL certificate settings

### Google Sheets API Error

**Symptoms:**
```
[ERROR] The caller does not have permission
```

**Solutions:**
- Verify Service Account has **Editor** permissions on the Spreadsheet
- Check if `SPREADSHEET_ID` is correct
- Ensure `credentials.json` file path is accurate
- Verify Google Sheets API is enabled in your project

### No Alerts Found

**Symptoms:**
```
[INFO] No new data to write.
```

**Solutions:**
- Check if `MIN_LEVEL` is too high (try lowering to 7 or 8)
- Verify `TIME_WINDOW_MINUTES` covers the expected alert period
- Confirm alerts exist in Wazuh for the specified time range
- Check Wazuh Indexer query in OpenSearch Dashboards

### Timeout Error

**Symptoms:**
```
[ERROR] Failed to connect to OpenSearch: Request timeout
```

**Solutions:**
- Increase timeout value in the script (default: 10 seconds)
- Check Wazuh Indexer performance and load
- Reduce `query["size"]` to fetch fewer alerts per request

## 🔒 Security Notes

### Best Practices

- ⚠️ **Never commit `credentials.json` to Git** - Add it to `.gitignore`
- ⚠️ **Use environment variables** for sensitive data in production
- ⚠️ **Keep your Wazuh password secure** - Consider using secrets management
- ⚠️ **Regularly rotate Service Account keys** - Follow Google's security guidelines
- ⚠️ **Restrict spreadsheet access** - Only share with necessary personnel
- ⚠️ **Use HTTPS** for all API communications
- ⚠️ **Monitor script execution logs** - Set up alerts for failures

### Recommended Security Enhancements

```python
# Use environment variables
import os
INDEXER_PASS = os.getenv('WAZUH_PASSWORD')
SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
```

### File Permissions

Set appropriate permissions for sensitive files:
```bash
chmod 600 credentials.json
chmod 700 wazuh_audit_logger.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add comments for complex logic
- Update README for new features
- Test thoroughly before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for the Security Community**

![Footer](./images/footer.png)
<!-- Add a footer image if desired -->
