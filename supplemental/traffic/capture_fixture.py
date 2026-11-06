#!/usr/bin/env python3
"""Capture real vnStat output in an isolated, disposable Linux CI environment.

Not a production installer. Run as an unprivileged user after installing vnstat.
Only interface names and aliases are anonymized; counters/dates/schema are real.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import threading
import time


def command(*args):
    result = subprocess.run(args, capture_output=True, timeout=3, check=True)
    if len(result.stdout) > 256 * 1024:
        raise RuntimeError("fixture exceeds proposed collector output limit")
    return result.stdout.decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError("fixture capture must run without root")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="beszel-vnstat-") as temp:
        root = Path(temp)
        db = root / "db"
        db.mkdir()
        cfg = root / "vnstat.conf"
        cfg.write_text(f'DatabaseDir "{db}"\nUseUTC 1\nUseLogging 0\n'
                       'UpdateInterval 2\nPollInterval 2\nSaveInterval 1\n'
                       'TrafficlessEntries 1\nAlwaysAddNewInterfaces 0\n')
        version = command("vnstat", "--version").strip()
        effective = command("vnstat", "--config", str(cfg), "--showconfig")
        assert any(line.split() == ["UseUTC", "1"] for line in effective.splitlines())
        zero = root / "non-utc.conf"
        zero.write_text(cfg.read_text().replace("UseUTC 1", "UseUTC 0"))
        rejected = command("vnstat", "--config", str(zero), "--showconfig")
        assert any(line.split() == ["UseUTC", "0"] for line in rejected.splitlines())
        command("vnstatd", "--config", str(cfg), "--initdb", "--noadd")
        names = sorted(p.name for p in Path("/sys/class/net").iterdir())
        selected = [name for name in names if name != "lo"][:1] + ["lo"]
        for name in selected:
            command("vnstat", "--config", str(cfg), "--add", "-i", name)
        with (root / "daemon.log").open("w") as log:
            daemon = subprocess.Popen(["vnstatd", "--config", str(cfg), "--nodaemon", "--noadd"],
                                      stdout=log, stderr=subprocess.STDOUT)
            try:
                time.sleep(4)
                if daemon.poll() is not None:
                    raise RuntimeError("isolated daemon exited before capture")
                # Actual loopback traffic, counted by the kernel and vnstatd.
                with socket.socket() as listener:
                    listener.bind(("127.0.0.1", 0))
                    listener.listen(1)
                    def receive():
                        connection, _ = listener.accept()
                        with connection:
                            while connection.recv(65536):
                                pass
                    reader = threading.Thread(target=receive)
                    reader.start()
                    with socket.create_connection(listener.getsockname(), timeout=3) as sender:
                        sender.sendall(b"x" * 262144)
                    reader.join(timeout=3)
                    assert not reader.is_alive()
                time.sleep(6)
            finally:
                if daemon.poll() is None:
                    daemon.send_signal(signal.SIGTERM)  # Flush this temporary DB only.
                daemon.wait(timeout=5)
        raw = command("vnstat", "--config", str(cfg), "--json", "d", "--limit", "0")
        data = json.loads(raw)
        assert "jsonversion" in data and data["interfaces"]
        bucket_count = 0
        for index, interface in enumerate(data["interfaces"]):
            interface["name"] = f"iface{index}"
            interface["alias"] = ""
            assert isinstance(interface["updated"]["timestamp"], int)
            for day in interface["traffic"]["day"]:
                assert isinstance(day["rx"], int) and isinstance(day["tx"], int)
                bucket_count += 1
        assert bucket_count > 0
        fixture = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        (output / "daily.json").write_text(fixture)
        keys = {"UseUTC", "DailyDays", "SaveInterval", "UpdateInterval", "TrafficlessEntries"}
        (output / "effective-config.txt").write_text("\n".join(
            line for line in effective.splitlines() if line.split() and line.split()[0] in keys) + "\n")
        (output / "non-utc-config.txt").write_text("\n".join(
            line for line in rejected.splitlines() if line.split() and line.split()[0] == "UseUTC") + "\n")
        summary = {
            "vnstat_version": version, "jsonversion": data["jsonversion"],
            "non_root": True, "daemon_config_matches_cli": True,
            "temporary_database_created_with_utc": True,
            "interfaces": len(data["interfaces"]), "daily_buckets": bucket_count,
            "original_json_bytes": len(raw.encode()),
            "sanitized_sha256": hashlib.sha256(fixture.encode()).hexdigest(),
            "command": "vnstat --config <isolated-config> --json d --limit 0",
            "anonymization": "interface names replaced; aliases cleared; counts and timestamps unchanged",
            "limits": "single-day CI data; not VPS permissions, 400-day capacity, or historical UTC proof",
        }
        (output / "provenance.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary))


if __name__ == "__main__":
    main()
