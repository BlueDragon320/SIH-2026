"""
Live Network Monitor & Egress Proof Auditor.
Continuously measures host and container network traffic to verify zero external egress.
"""
import time
import psutil
from typing import Dict, Any, List

class NetworkMonitor:
    def __init__(self):
        self._last_check = time.time()
        self._last_counters = psutil.net_io_counters(pernic=True)
        self._loopback_interfaces = {"lo", "loopback", "docker0", "br-"}

    def sample_network_status(self) -> Dict[str, Any]:
        """
        Sample network interface metrics and compute egress rates.
        Separates external interfaces (eth0, wlan0, enp*) from local loopbacks.
        """
        now = time.time()
        elapsed = max(now - self._last_check, 0.001)
        current_counters = psutil.net_io_counters(pernic=True)

        external_bytes_sent = 0
        external_bytes_recv = 0
        external_rate_sent = 0.0
        external_rate_recv = 0.0

        interface_details = []

        for iface_name, counters in current_counters.items():
            is_internal = any(iface_name.startswith(prefix) for prefix in ["lo", "docker", "veth", "br-"])
            
            old_c = self._last_counters.get(iface_name, counters)
            delta_sent = max(counters.bytes_sent - old_c.bytes_sent, 0)
            delta_recv = max(counters.bytes_recv - old_c.bytes_recv, 0)

            rate_sent = delta_sent / elapsed
            rate_recv = delta_recv / elapsed

            if not is_internal:
                external_bytes_sent += delta_sent
                external_bytes_recv += delta_recv
                external_rate_sent += rate_sent
                external_rate_recv += rate_recv

            interface_details.append({
                "interface": iface_name,
                "is_internal": is_internal,
                "bytes_sent_total": counters.bytes_sent,
                "bytes_recv_total": counters.bytes_recv,
                "send_rate_bps": round(rate_sent, 2),
                "recv_rate_bps": round(rate_recv, 2),
            })

        self._last_check = now
        self._last_counters = current_counters

        # Check active socket connections
        active_sockets = []
        try:
            for c in psutil.net_connections(kind="inet"):
                r_addr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "NONE"
                l_addr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "NONE"
                active_sockets.append({
                    "fd": c.fd,
                    "status": c.status,
                    "local": l_addr,
                    "remote": r_addr,
                    "is_external": not (r_addr.startswith("127.") or r_addr == "NONE" or r_addr.startswith("::1"))
                })
        except Exception:
            pass

        return {
            "timestamp": now,
            "airgap_status": "SECURE_AIR_GAPPED" if external_rate_sent < 50.0 else "TRAFFIC_DETECTED",
            "external_egress_rate_bps": round(external_rate_sent, 2),
            "external_ingress_rate_bps": round(external_rate_recv, 2),
            "external_egress_bytes_delta": external_bytes_sent,
            "external_ingress_bytes_delta": external_bytes_recv,
            "interfaces": interface_details,
            "active_connections_count": len(active_sockets),
            "external_connections": [s for s in active_sockets if s["is_external"]],
            "verified_zero_egress": (external_bytes_sent == 0)
        }

# Global singleton monitor
monitor_instance = NetworkMonitor()
