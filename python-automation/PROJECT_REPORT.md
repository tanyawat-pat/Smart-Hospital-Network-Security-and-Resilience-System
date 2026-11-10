# Smart Hospital Network Automation
## Final Project Report

### 1. Project Overview
The Smart Hospital Network Automation project aims to design and simulate a reliable hospital network infrastructure using Cisco Packet Tracer and Python automation.

The project provides network segmentation, centralized management, network monitoring, and backup connectivity to support hospital operations.

### 2. Project Objectives
- Design a structured hospital network.
- Separate departments using VLAN technology.
- Provide automatic IP address allocation using DHCP.
- Enable communication between VLANs through inter-VLAN routing.
- Implement OSPF routing.
- Configure and test network failover.
- Integrate a Network Controller with Python using REST API.
- Develop a monitoring dashboard using Streamlit.

### 3. Network Infrastructure

| Device | Role |
|---|---|
| R1 | Main Router |
| R2 | Secondary Router |
| R3 | Additional Router |
| SW1 | Network Switch |
| PT-Controller | Network Management |
| Admin PC | Network Administration |

### 4. VLAN Configuration

| VLAN | Department |
|---|---|
| VLAN 10 | Doctor / Nurse |
| VLAN 20 | Administration |
| VLAN 30 | IoT |
| VLAN 40 | Guest |
| VLAN 99 | Management |

### 5. IP Addressing Plan

| Network | Gateway |
|---|---|
| VLAN 10 | 192.168.10.1 |
| VLAN 20 | 192.168.20.1 |
| VLAN 30 | 192.168.30.1 |
| VLAN 40 | 192.168.40.1 |
| VLAN 99 | 192.168.99.1 |

Network Controller:
- IP Address: 192.168.99.10
- Default Gateway: 192.168.99.1
- REST API Port: 58000

### 6. Routing and Failover
OSPF is used to exchange routing information between routers.

The network includes a primary path and a backup path.

Failover testing was performed by disabling the primary path and verifying that network traffic could use the backup path.

**Test Result:** Successful, according to the project test.

### 7. Python Automation
Python and the Requests library are used to communicate with the Network Controller REST API.

The automation program:
- Requests an authentication ticket.
- Uses the ticket to access the Controller API.
- Retrieves the available API response.
- Saves monitoring results in JSON format.

### 8. Monitoring Dashboard
The Streamlit dashboard provides:
- Network Controller status
- REST API status
- Router interface information
- Interface UP / DOWN summary
- Network Health Chart
- Network Alerts
- Monitoring History
- Failover Event Log
- Report download

### 9. Testing Results

| Test | Result |
|---|---|
| Controller Login | Successful |
| REST API Connection | Successful |
| Router Interface Inspection | Completed |
| Router Monitoring Dashboard | Displayed |
| Interface DOWN Alert | Displayed |
| OSPF Failover Test | Successful |
| Monitoring Report Export | Available |

### 10. Limitations
- Router interface information is currently stored as a configuration snapshot from Packet Tracer CLI.
- Router monitoring is not yet real-time.
- Failover events are recorded manually after testing.
- The Controller API response does not currently provide discovered router information in the tested endpoint.

### 11. Conclusion
The Smart Hospital Network Automation project demonstrates network segmentation, routing, failover, Controller API integration, and a Python-based monitoring dashboard.

The project provides a foundation for further development toward automated hospital network management and monitoring.

### 12. Future Improvements
- Real-time router monitoring.
- Automatic failover event detection.
- Automated email or notification alerts.
- Extended network performance analysis.
- Integration with additional network management systems.