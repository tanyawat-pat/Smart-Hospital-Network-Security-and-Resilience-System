import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Hospital | Network Operations Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# THEME / STYLES
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --navy: #10243A;
        --navy-2: #173852;
        --teal: #19A7A0;
        --teal-soft: #E7F6F4;
        --blue-soft: #EAF2FA;
        --ink: #172B3A;
        --muted: #647789;
        --line: #E3EAF0;
        --surface: #FFFFFF;
        --page: #F4F7FA;
        --red: #C94B4B;
        --amber: #C58A25;
        --green: #21845B;
    }

    .stApp { background: var(--page); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(244,247,250,.92); }
    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
    }
    [data-testid="stSidebar"] {
        background: var(--navy);
        border-right: 1px solid #203D55;
    }
    [data-testid="stSidebar"] * { color: #EAF2F7 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #BFD0DD !important;
    }
    .hero {
        background: linear-gradient(115deg, #10243A 0%, #173F5C 65%, #146E78 100%);
        border-radius: 18px;
        padding: 27px 30px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 10px 28px rgba(16,36,58,.12);
    }
    .hero-kicker {
        color: #8FE0D5;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .hero h1 {
        color: white !important;
        font-size: 29px !important;
        line-height: 1.2;
        margin: 0 !important;
        font-weight: 800;
    }
    .hero p {
        color: #D5E4ED !important;
        margin: 8px 0 0 0 !important;
        font-size: 14px;
    }
    .section-heading {
        color: var(--navy);
        font-weight: 800;
        font-size: 19px;
        margin: 4px 0 2px 0;
    }
    .section-note {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 12px;
    }
    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 3px 12px rgba(16,36,58,.035);
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] {
        color: var(--navy);
        font-weight: 800;
    }
    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
    }
    .status-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .4px;
    }
    .pill-green { color: #176B49; background: #E5F5ED; }
    .pill-red { color: #A73535; background: #FCEAEA; }
    .pill-amber { color: #8B6119; background: #FFF4DC; }
    .info-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 95px;
    }
    .info-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
    }
    .info-value {
        color: var(--navy);
        font-size: 22px;
        font-weight: 800;
        margin-top: 5px;
    }
    .footer {
        text-align: center;
        color: #8293A1;
        font-size: 11px;
        padding: 26px 0 4px 0;
    }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 9px;
        font-weight: 700;
        min-height: 40px;
    }
    hr { border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# FILES / DATA
# =========================================================
REPORT_FILE = "monitoring_report.json"
ROUTER_FILE = "router_data.json"
HISTORY_FILE = "monitoring_history.csv"
FAILOVER_FILE = "failover_history.csv"


def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else default
    except (json.JSONDecodeError, OSError, TypeError):
        st.warning(f"Could not read {filename}. The dashboard will use an empty data set.")
        return default


def load_csv(filename):
    if not os.path.exists(filename):
        return pd.DataFrame()
    try:
        return pd.read_csv(filename)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        st.warning(f"Could not read {filename}.")
        return pd.DataFrame()


def save_csv_record(filename, record):
    new_row = pd.DataFrame([record])
    old_rows = load_csv(filename)
    result = pd.concat([old_rows, new_row], ignore_index=True) if not old_rows.empty else new_row
    result.to_csv(filename, index=False)
    return result


report = load_json(REPORT_FILE, {})
router_data = load_json(ROUTER_FILE, {"routers": []})
routers = router_data.get("routers", [])
if not isinstance(routers, list):
    routers = []

# Flatten router interfaces while retaining the router name.
all_interfaces = []
for router in routers:
    if not isinstance(router, dict):
        continue
    for interface in router.get("interfaces", []) or []:
        if not isinstance(interface, dict):
            continue
        all_interfaces.append(
            {
                "Router": router.get("name", "Unknown"),
                "Interface": interface.get("interface", "Unknown"),
                "IP Address": interface.get("ip", "Unknown"),
                "Status": str(interface.get("status", "Unknown")).upper(),
            }
        )

total_routers = len(routers)
total_interfaces = len(all_interfaces)
up_interfaces = sum(row["Status"] == "UP" for row in all_interfaces)
down_interfaces = sum(row["Status"] == "DOWN" for row in all_interfaces)
unknown_interfaces = total_interfaces - up_interfaces - down_interfaces
health_pct = (up_interfaces / total_interfaces * 100) if total_interfaces else 0

# These fields reflect the HTTP result recorded by the existing controller script.
controller_online = report.get("controller_status") == 201
api_reachable = report.get("network_device_status") == 200

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🏥 SMART HOSPITAL")
    st.markdown("### Network Operations Center")
    st.caption("PROJECT MONITORING")
    st.divider()
    st.markdown("**Dashboard navigation**")
    st.markdown("- System Overview")
    st.markdown("- Router Monitoring")
    st.markdown("- Network Alerts")
    st.markdown("- Monitoring History")
    st.markdown("- Failover Records")
    st.divider()
    st.caption("Data files")
    st.code("router_data.json\nmonitoring_report.json", language="text")
    st.caption("Snapshot-based monitoring. Refresh reloads the local data files.")

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Network Operations Center</div>
        <h1>Smart Hospital Network</h1>
        <p>Centralized view of router interfaces, controller connectivity, network health and failover test records.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([4, 1])
with top_left:
    st.caption(f"Last dashboard render: {datetime.now().strftime('%d %b %Y  |  %H:%M:%S')}")
with top_right:
    if st.button("↻  Refresh dashboard", use_container_width=True):
        st.rerun()

# Data quality note: do not imply live polling where data is a saved snapshot.
if not os.path.exists(ROUTER_FILE):
    st.warning("router_data.json was not found. Add the router snapshot file to the dashboard folder to display interface information.")
else:
    st.info("Monitoring data is based on the saved router snapshot. Interface status is not being polled live from Packet Tracer.")

# =========================================================
# SYSTEM OVERVIEW
# =========================================================
st.markdown('<div class="section-heading">System overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">At-a-glance status from the available monitoring files</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Routers recorded", total_routers)
m2.metric("Interfaces UP", up_interfaces, help="Count of interfaces marked UP in router_data.json")
m3.metric("Interfaces DOWN", down_interfaces, help="Count of interfaces marked DOWN in router_data.json")
m4.metric("Interface availability", f"{health_pct:.1f}%" if total_interfaces else "N/A")

s1, s2 = st.columns(2)
with s1:
    controller_label = "Ticket created" if controller_online else "Not confirmed"
    controller_class = "pill-green" if controller_online else "pill-amber"
    st.markdown(
        f'<div class="info-card"><div class="info-label">PT-Controller REST ticket</div>'
        f'<div class="info-value">{controller_label}</div>'
        f'<span class="status-pill {controller_class}">HTTP {report.get("controller_status", "N/A")}</span></div>',
        unsafe_allow_html=True,
    )
with s2:
    api_label = "Endpoint responded" if api_reachable else "Not confirmed"
    api_class = "pill-green" if api_reachable else "pill-amber"
    st.markdown(
        f'<div class="info-card"><div class="info-label">REST API request</div>'
        f'<div class="info-value">{api_label}</div>'
        f'<span class="status-pill {api_class}">HTTP {report.get("network_device_status", "N/A")}</span></div>',
        unsafe_allow_html=True,
    )
st.caption("A successful REST API response confirms that the endpoint responded; it does not necessarily mean device inventory was returned.")

st.divider()

# =========================================================
# NETWORK HEALTH
# =========================================================
st.markdown('<div class="section-heading">Network health</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Distribution of interface states across the recorded routers</div>', unsafe_allow_html=True)

health_col, summary_col = st.columns([1.45, 1])
with health_col:
    if total_interfaces:
        chart_df = pd.DataFrame(
            {"Interface count": [up_interfaces, down_interfaces, unknown_interfaces]},
            index=["UP", "DOWN", "UNKNOWN"],
        )
        st.bar_chart(chart_df, height=260)
    else:
        st.info("No interface records are available yet.")
with summary_col:
    st.metric("Total interfaces", total_interfaces)
    if down_interfaces:
        st.error(f"{down_interfaces} interface(s) are marked DOWN.")
    elif unknown_interfaces:
        st.warning(f"{unknown_interfaces} interface(s) have an unknown status.")
    elif total_interfaces:
        st.success("All recorded interfaces are marked UP.")
    else:
        st.info("Add router interface records to calculate network health.")

st.divider()

# =========================================================
# ROUTER MONITORING
# =========================================================
st.markdown('<div class="section-heading">Router monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Interface, IP address and recorded status for each router</div>', unsafe_allow_html=True)

if routers:
    for router in routers:
        if not isinstance(router, dict):
            continue
        router_name = router.get("name", "Unknown")
        interfaces = router.get("interfaces", []) or []
        router_up = sum(str(item.get("status", "")).upper() == "UP" for item in interfaces if isinstance(item, dict))
        router_down = sum(str(item.get("status", "")).upper() == "DOWN" for item in interfaces if isinstance(item, dict))
        with st.expander(f"{router_name}     •     {router_up} UP     •     {router_down} DOWN", expanded=True):
            if interfaces:
                frame = pd.DataFrame(interfaces)
                frame = frame.rename(
                    columns={
                        "interface": "Interface",
                        "ip": "IP Address",
                        "status": "Status",
                    }
                )
                keep = [c for c in ["Interface", "IP Address", "Status"] if c in frame.columns]
                if keep:
                    st.dataframe(frame[keep], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(frame, use_container_width=True, hide_index=True)
            else:
                st.caption("No interfaces recorded for this router.")
else:
    st.info("No router records found in router_data.json.")

st.divider()

# =========================================================
# ALERTS
# =========================================================
st.markdown('<div class="section-heading">Network alerts</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Interfaces that are DOWN or have an unknown state</div>', unsafe_allow_html=True)

alerts = [row for row in all_interfaces if row["Status"] != "UP"]
if alerts:
    alert_df = pd.DataFrame(alerts)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    if total_interfaces:
        st.success("No DOWN or UNKNOWN interface states were found in the saved snapshot.")
    else:
        st.info("No interface data is available for alert checking.")

st.divider()

# =========================================================
# MONITORING HISTORY
# =========================================================
st.markdown('<div class="section-heading">Monitoring history</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Save a manual snapshot and review previous records</div>', unsafe_allow_html=True)

if st.button("＋  Save current snapshot", type="primary"):
    history = save_csv_record(
        HISTORY_FILE,
        {
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Routers": total_routers,
            "Total Interfaces": total_interfaces,
            "Interfaces UP": up_interfaces,
            "Interfaces DOWN": down_interfaces,
            "Unknown Interfaces": unknown_interfaces,
            "Availability (%)": round(health_pct, 1),
        },
    )
    st.success("Snapshot saved to monitoring_history.csv.")
    st.rerun()

history_df = load_csv(HISTORY_FILE)
if not history_df.empty:
    st.dataframe(history_df.tail(10), use_container_width=True, hide_index=True)
    if len(history_df) >= 2 and {"Time", "Interfaces UP", "Interfaces DOWN"}.issubset(history_df.columns):
        st.markdown("**Recent interface trend**")
        trend = history_df.tail(20).copy().set_index("Time")
        st.line_chart(trend[["Interfaces UP", "Interfaces DOWN"]], height=250)
    st.download_button(
        "Download monitoring history",
        data=history_df.to_csv(index=False).encode("utf-8"),
        file_name="monitoring_history.csv",
        mime="text/csv",
    )
else:
    st.info("No monitoring history has been saved. Select “Save current snapshot” to create the first record.")

st.divider()

# =========================================================
# FAILOVER RECORDS
# =========================================================
st.markdown('<div class="section-heading">Failover test records</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Manually record a failover test after verifying the backup path in Packet Tracer</div>', unsafe_allow_html=True)

with st.form("failover_form"):
    failover_result = st.selectbox("Test result", ["SUCCESS", "FAILED", "INCONCLUSIVE"])
    failover_note = st.text_input("Test note (optional)", placeholder="Example: Primary link disabled; backup route restored connectivity")
    submitted = st.form_submit_button("＋  Save failover test record", type="primary")

if submitted:
    save_csv_record(
        FAILOVER_FILE,
        {
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Event": "Primary Path Failure Test",
            "Action": "Checked backup network path",
            "Result": failover_result,
            "Notes": failover_note,
        },
    )
    st.success("Failover test record saved.")
    st.rerun()

failover_df = load_csv(FAILOVER_FILE)
if not failover_df.empty:
    st.dataframe(failover_df.tail(20), use_container_width=True, hide_index=True)
    st.download_button(
        "Download failover history",
        data=failover_df.to_csv(index=False).encode("utf-8"),
        file_name="failover_history.csv",
        mime="text/csv",
    )
else:
    st.info("No failover test records have been saved yet.")

st.divider()

# =========================================================
# REPORT EXPORT
# =========================================================
st.markdown('<div class="section-heading">Reports & export</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Export the available snapshot and controller response data</div>', unsafe_allow_html=True)

full_report = {
    "project": "Smart Hospital Network Monitoring",
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data_note": "Router interface values are based on the saved snapshot, not live polling.",
    "controller_report": report,
    "router_data": router_data,
    "summary": {
        "total_routers": total_routers,
        "total_interfaces": total_interfaces,
        "interfaces_up": up_interfaces,
        "interfaces_down": down_interfaces,
        "unknown_interfaces": unknown_interfaces,
        "availability_percent": round(health_pct, 1),
    },
}
st.download_button(
    "↓  Download full network report (JSON)",
    data=json.dumps(full_report, indent=4, ensure_ascii=False).encode("utf-8"),
    file_name="smart_hospital_full_report.json",
    mime="application/json",
)

st.markdown(
    """
    <div class="footer">
        SMART HOSPITAL NETWORK AUTOMATION PROJECT<br>
        Network Monitoring Dashboard · Snapshot-based monitoring
    </div>
    """,
    unsafe_allow_html=True,
)
