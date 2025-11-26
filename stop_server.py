#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time

PORT = 8082


def find_pids_by_port(port: int):
    """Return a set of PIDs listening on the given TCP port."""
    pids = set()
    try:
        out = subprocess.check_output(["lsof", "-t", f"-i:{port}"], text=True)
        for line in out.strip().splitlines():
            if line.strip():
                pids.add(int(line.strip()))
    except subprocess.CalledProcessError:
        # No process found or lsof returned non-zero
        pass
    except FileNotFoundError:
        # lsof not available; fallback later
        pass
    return pids


def find_uvicorn_pids():
    """Return a set of PIDs that look like uvicorn processes for app.main:app or run_server.py."""
    pids = set()
    try:
        out = subprocess.check_output(["ps", "aux"], text=True)
        for line in out.splitlines():
            if "uvicorn" in line and ("app.main:app" in line or "run_server.py" in line):
                parts = line.split()
                if parts:
                    try:
                        pids.add(int(parts[1]))
                    except Exception:
                        pass
    except Exception:
        pass
    return pids


def kill_pids(pids):
    if not pids:
        return False
    # Send SIGTERM first
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to PID {pid}")
        except ProcessLookupError:
            pass
        except PermissionError:
            print(f"Permission denied when terminating PID {pid}")
    # Wait briefly
    time.sleep(1.0)
    # Check remaining
    remaining = set()
    for pid in pids:
        try:
            os.kill(pid, 0)
            remaining.add(pid)
        except ProcessLookupError:
            pass
    # Escalate to SIGKILL if needed
    for pid in remaining:
        try:
            os.kill(pid, signal.SIGKILL)
            print(f"Sent SIGKILL to PID {pid}")
        except ProcessLookupError:
            pass
        except PermissionError:
            print(f"Permission denied when killing PID {pid}")
    return True


def main():
    # Try by port 8082
    pids = find_pids_by_port(PORT)
    if pids:
        print(f"Found processes on port {PORT}: {sorted(pids)}")
        kill_pids(pids)
        sys.exit(0)
    # Fallback: try matching uvicorn command line
    pids = find_uvicorn_pids()
    if pids:
        print(f"Found uvicorn-like processes: {sorted(pids)}")
        kill_pids(pids)
        sys.exit(0)
    print("No server process found (port 8082 free and no matching uvicorn process).")
    sys.exit(0)


if __name__ == "__main__":
    main()

