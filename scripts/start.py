#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Career Planning Agent - Service Launcher
Start backend and frontend services
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
        return None

def kill_process(pid):
    """Kill process by PID"""
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(f"  Killed process {pid}")
        return True
    except Exception as e:
        return False

def stop_existing():
    """Stop any existing services"""
    print("[1/4] Checking for existing services...")

    backend_pid = get_process_on_port(8000)
    if backend_pid:
        kill_process(backend_pid)
    else:
        print("  Backend not running")

    frontend_pid = get_process_on_port(3000)
    if frontend_pid:
        kill_process(frontend_pid)
        return

    for port in [3001, 3002]:
        frontend_pid = get_process_on_port(port)
        if frontend_pid:
            kill_process(frontend_pid)
            return

    print("  Frontend not running")
    print("  Waiting for ports to be released...")
    time.sleep(2)

def start_services():
    """Start backend and frontend"""
    print()
    print("[2/4] Creating log directory...")
    log_dir = os.path.join(ROOT_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    print(f"  Log directory: {log_dir}")

    print()
    print("[3/4] Starting backend...")
    backend_script = os.path.join(ROOT_DIR, 'app', 'backend', 'api_server.py')
    subprocess.Popen(
        ['python', backend_script],
        cwd=ROOT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    print("  Waiting for backend...")
    time.sleep(3)

    print()
    print("[4/4] Starting frontend...")
    frontend_dir = os.path.join(ROOT_DIR, 'app', 'frontend_optimized')
    subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

def print_status():
    """Print status"""
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
    print("  Career Planning Agent - Start")
    print("=" * 50)
    print()

    stop_existing()
    start_services()
    print_status()

    input("Press Enter to exit...")

if __name__ == '__main__':
    main()
