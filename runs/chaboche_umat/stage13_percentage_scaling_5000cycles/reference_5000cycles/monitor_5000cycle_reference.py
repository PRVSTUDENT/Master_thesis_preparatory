from __future__ import print_function

from pathlib import Path
import os
import re
import sys
import time


JOB = "chaboche_vp_v1_cyclic_eps005_5000cycles"
STA = Path(JOB + ".sta")
ODB = Path(JOB + ".odb")
TARGET_TIME = 5000.0
BAR_WIDTH = 48


def tail_lines(path, count=24):
    if not path.exists():
        return []
    return path.read_text(errors="ignore").splitlines()[-count:]


def latest_step_time(lines):
    latest = None
    for line in lines:
        parts = line.split()
        if len(parts) >= 8 and parts[0].isdigit() and parts[1].isdigit():
            try:
                latest = float(parts[6])
            except ValueError:
                pass
    return latest


def human_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return "%.1f %s" % (value, unit)
        value /= 1024.0


def render():
    lines = tail_lines(STA)
    step_time = latest_step_time(lines)
    if step_time is None:
        percent = 0.0
        filled = 0
        remaining = TARGET_TIME
    else:
        percent = max(0.0, min(100.0, 100.0 * step_time / TARGET_TIME))
        filled = int(round(BAR_WIDTH * percent / 100.0))
        remaining = max(0.0, TARGET_TIME - step_time)

    bar = "#" * filled + "-" * (BAR_WIDTH - filled)
    odb_info = "missing"
    if ODB.exists():
        stat = ODB.stat()
        odb_info = "%s, modified %s" % (
            human_size(stat.st_size),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        )

    os.system("clear")
    print("Abaqus HPC progress monitor")
    print("Job: %s" % JOB)
    print("STA: %s" % STA)
    print("[%s] %6.2f%%" % (bar, percent))
    if step_time is None:
        print("Current step time : waiting for .sta data")
    else:
        print("Current step time : %.4f" % step_time)
    print("Total target time : %.4f" % TARGET_TIME)
    print("Remaining time    : %.4f" % remaining)
    print("ODB               : %s" % odb_info)
    print("")
    print("--- Last .sta lines ---")
    for line in lines[-12:]:
        print(line)
    print("")
    print("Press Ctrl+C to stop monitoring. The Abaqus job will keep running.")
    sys.stdout.flush()


def main():
    try:
        while True:
            render()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped monitor.")


if __name__ == "__main__":
    main()
