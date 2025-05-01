import socket
import subprocess
import platform
import traceback
import httpx
import time
from urllib.parse import urlparse

def check_connectivity(url, timeout=5):
    """
    Check connectivity to a URL and return diagnostic information
    
    Args:
        url (str): The URL to check
        timeout (int): Timeout in seconds
        
    Returns:
        dict: Dictionary with diagnostic information
    """
    result = {
        "url": url,
        "reachable": False,
        "error": None,
        "dns_resolution": None,
        "ping_result": None,
        "http_status": None,
        "response_time": None,
        "traceroute": None
    }
    
    # Parse URL
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc.split(':')[0]
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    except Exception as e:
        result["error"] = f"URL parsing error: {str(e)}"
        return result
    
    # DNS resolution
    try:
        start_time = time.time()
        ip_address = socket.gethostbyname(hostname)
        result["dns_resolution"] = {
            "hostname": hostname,
            "ip_address": ip_address,
            "time_ms": round((time.time() - start_time) * 1000, 2)
        }
    except socket.gaierror as e:
        result["error"] = f"DNS resolution error: {str(e)}"
        return result
    
    # Socket connection test
    try:
        start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((hostname, port))
        s.close()
        result["socket_connection"] = {
            "success": True,
            "time_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        result["socket_connection"] = {
            "success": False,
            "error": str(e)
        }
        result["error"] = f"Socket connection error: {str(e)}"
        return result
    
    # Ping test
    try:
        ping_param = "-n" if platform.system().lower() == "windows" else "-c"
        ping_cmd = ["ping", ping_param, "1", hostname]
        ping_output = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=timeout)
        result["ping_result"] = {
            "command": " ".join(ping_cmd),
            "exit_code": ping_output.returncode,
            "output": ping_output.stdout
        }
    except Exception as e:
        result["ping_result"] = {
            "error": str(e)
        }
    
    # HTTP request
    try:
        start_time = time.time()
        response = httpx.get(url, timeout=timeout)
        result["http_status"] = response.status_code
        result["response_time"] = round((time.time() - start_time) * 1000, 2)
        result["reachable"] = response.status_code < 400
    except Exception as e:
        result["error"] = f"HTTP request error: {str(e)}"
    
    return result

def diagnose_connection(url):
    """
    Run diagnostics on a URL and return a formatted report
    
    Args:
        url (str): The URL to diagnose
        
    Returns:
        str: Formatted diagnostic report
    """
    print(f"Running network diagnostics for {url}...")
    
    try:
        result = check_connectivity(url)
        
        # Format report
        report = [f"Network Diagnostics for {url}:"]
        report.append("-" * 50)
        
        if result["reachable"]:
            report.append("✅ URL is reachable")
        else:
            report.append("❌ URL is not reachable")
        
        if result["error"]:
            report.append(f"Error: {result['error']}")
        
        if result["dns_resolution"]:
            dns = result["dns_resolution"]
            report.append(f"DNS Resolution: {dns['hostname']} → {dns['ip_address']} ({dns['time_ms']}ms)")
        
        if "socket_connection" in result:
            socket_conn = result["socket_connection"]
            if socket_conn["success"]:
                report.append(f"Socket Connection: Success ({socket_conn['time_ms']}ms)")
            else:
                report.append(f"Socket Connection: Failed - {socket_conn['error']}")
        
        if result["ping_result"]:
            ping = result["ping_result"]
            if "error" in ping:
                report.append(f"Ping: Failed - {ping['error']}")
            else:
                status = "Success" if ping["exit_code"] == 0 else "Failed"
                report.append(f"Ping: {status} (exit code: {ping['exit_code']})")
                # Include first line of ping output
                if ping["output"]:
                    first_line = ping["output"].strip().split('\n')[0]
                    report.append(f"  {first_line}")
        
        if result["http_status"]:
            report.append(f"HTTP Status: {result['http_status']} ({result['response_time']}ms)")
        
        return "\n".join(report)
    
    except Exception as e:
        return f"Diagnostic error: {str(e)}\n{traceback.format_exc()}"
