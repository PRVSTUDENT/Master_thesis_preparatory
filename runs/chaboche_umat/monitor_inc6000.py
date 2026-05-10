from __future__ import print_function
import os
import re
import sys
import time

JOB = "chaboche_eps005_20cycles_dtmax_0p005_inc6000"
STA = JOB + ".sta"
MSG = JOB + ".msg"
DAT = JOB + ".dat"

TOTAL_TIME = 20.0
MAX_INC = 6000
BAR_WIDTH = 40
POLL_SECONDS = 10

def read_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", errors="ignore") as f:
        return f.read()

def latest_status_from_sta(text):
    latest_inc = None
    latest_time = None

    for line in text.splitlines():
        parts = line.split()
        nums = []
        for p in parts:
            try:
                nums.append(float(p.replace("D", "E")))
            except Exception:
                pass

        if len(nums) >= 2:
            try:
                inc_candidate = int(nums[0])
            except Exception:
                inc_candidate = None
            time_candidates = [x for x in nums if 0.0 <= x <= TOTAL_TIME]
            if inc_candidate is not None and time_candidates:
                latest_inc = inc_candidate
                latest_time = max(time_candidates)

    return latest_inc, latest_time

def progress_bar(frac):
    frac = max(0.0, min(1.0, frac))
    filled = int(round(frac * BAR_WIDTH))
    return "[" + "#" * filled + "-" * (BAR_WIDTH - filled) + "]"

def terminal_state():
    msg = read_text(MSG)
    dat = read_text(DAT)

    combined = msg + "\n" + dat

    if "TOO MANY INCREMENTS NEEDED TO COMPLETE THE STEP" in combined:
        return "too_many_increments"

    if "THE ANALYSIS HAS BEEN COMPLETED" in combined:
        return "completed"

    if "THE ANALYSIS HAS NOT BEEN COMPLETED" in combined:
        return "not_completed"

    if "Abaqus/Standard Analysis exited with an error" in combined:
        return "error"

    return "running"

def main():
    print("Monitoring:", JOB)
    print("Press Ctrl+C to stop monitor only; it will not stop Abaqus.")
    print("")

    while True:
        state = terminal_state()
        sta = read_text(STA)
        inc, step_time = latest_status_from_sta(sta)

        if step_time is None:
            frac = 0.0
            step_time = 0.0
        else:
            frac = step_time / TOTAL_TIME

        if inc is None:
            inc = 0

        bar = progress_bar(frac)
        pct = frac * 100.0

        sys.stdout.write(
            "\r%s %6.2f%% | step_time=%8.4f/%s | inc=%s/%s | state=%s"
            % (bar, pct, step_time, TOTAL_TIME, inc, MAX_INC, state)
        )
        sys.stdout.flush()

        if state in ("completed", "too_many_increments", "not_completed", "error"):
            print("\nFinal state:", state)
            break

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
