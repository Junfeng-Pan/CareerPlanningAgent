#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Career Planning Agent - Service Manager
Start, stop, and restart backend and frontend services
"""
import os
import sys
import subprocess
import time
import signal

# Get project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def get_process_on_port(port):
    """Find PID of process listening on given port"""
    try:
        import socket
        # Use netstat via subprocess
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    return parts[-1]
        return None
    except Exception as e:
        print(f"Error finding process on port {port}: {e}")
        return None

def kill_process(pid):
    """Kill process by PID"""
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(f"  Killed process {pid}")
        return True
    except Exception as e:
        print(f"  Failed to kill {pid}: {e}")
        return False

def stop_services():
    """Stop backend and frontend services"""
    print("[1/4] Stopping services...")

    # Find and kill backend
    backend_pid = get_process_on_port(8000)
    if backend_pid:
        kill_process(backend_pid)
    else:
        print("  Backend not running")

    # Find and kill frontend
    frontend_pid = get_process_on_port(3000)
    if frontend_pid:
        kill_process(frontend_pid)
    else:
        # Try other common ports (3001, 3002)
        for port in [3001, 3002]:
            frontend_pid = get_process_on_port(port)
            if frontend_pid:
                kill_process(frontend_pid)
                break
        else:
            print("  Frontend not running")

    # Wait for ports to be released
    print("  Waiting for ports to be released...")
    time.sleep(2)

def clear_logs():
    """Clear log files"""
    print("[2/4] Clearing logs...")
    log_path = os.path.join(ROOT_DIR, 'logs', 'api_server.log')
    try:
        if os.path.exists(log_path):
            os.remove(log_path)
            print("  Logs cleared")
        else:
            print("  No logs to clear")
    except Exception as e:
        print(f"  Error clearing logs: {e}")

def start_backend():
    """Start backend service"""
    print("[3/4] Starting backend...")

    # Create log directory
    log_dir = os.path.join(ROOT_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Start backend in new window
    backend_script = os.path.join(ROOT_DIR, 'app', 'backend', 'api_server.py')
    subprocess.Popen(
        ['python', backend_script],
        cwd=ROOT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("  Waiting for backend to initialize...")
    time.sleep(3)

    # Check if backend started
    if get_process_on_port(8000):
        print("  Backend started successfully")
        return True
    else:
        print("  WARNING: Backend may not have started")
        return False

def start_frontend():
    """Start frontend service"""
    print("[4/4] Starting frontend...")

    frontend_dir = os.path.join(ROOT_DIR, 'app', 'frontend_optimized')

    # Start frontend in new window
    subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("  Frontend starting...")

def print_status():
    """Print service status"""
    print()
    print("=" * 50)
    print("  Services started!")
    print("=" * 50)
    print()
    print("  Backend API:  http://localhost:8000")
    print("  Frontend:     http://localhost:3000")
    print(f"  Log file:     {ROOT_DIR}\\logs\\api_server.log")
    print()

def main():
    print()
    print("=" * 50)
    print("  Career Planning Agent - Restart")
    print("=" * 50)
    print()

    stop_services()
    clear_logs()
    start_backend()
    start_frontend()
    print_status()

    input("Press Enter to exit...")

if __name__ == '__main__':
    main()
