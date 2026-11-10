
import requests
import json
from getpass import getpass
from datetime import datetime

BASE_URL = "http://localhost:58000/api/v1"

username = input("Username: ")
password = getpass("Password: ")

# Login Controller
login = requests.post(
    f"{BASE_URL}/ticket",
    json={
        "username": username,
        "password": password
    },
    timeout=10
)

report = {
    "project": "Smart Hospital Network Monitoring",
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "controller_status": login.status_code
}

if login.status_code == 201:
    ticket = login.json()["response"]["serviceTicket"]

    headers = {"X-Auth-Token": ticket}

    result = requests.get(
        f"{BASE_URL}/network-device",
        headers=headers,
        timeout=10
    )

    report["network_device_status"] = result.status_code
    report["network_device_data"] = result.json()

else:
    report["error"] = login.text

# Save report
with open("monitoring_report.json", "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4, ensure_ascii=False)

print("\n===== SMART HOSPITAL MONITORING =====")
print(json.dumps(report, indent=4, ensure_ascii=False))
print("\nReport saved: monitoring_report.json")
