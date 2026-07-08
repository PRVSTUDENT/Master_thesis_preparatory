from __future__ import print_function

import os
import time


JOB = "chaboche_vp_v1_cyclic_eps005_50cycles"
STA_PATH = JOB + ".sta"
TOTAL_TIME = 50.0
MAX_INC = 6000


def parse_sta():
    if not os.path.exists(STA_PATH):
        return None
    last = None
    with open(STA_PATH, "r") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 7 and parts[0].isdigit():
                try:
                    last = {
                        "step": int(parts[0]),
                        "inc": int(parts[1]),
                        "step_time": float(parts[6]),
                    }
                except Exception:
                    pass
    return last


def bar(progress, width=40):
    progress = max(0.0, min(1.0, progress))
    filled = int(progress * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main():
    print("Monitoring %s" % STA_PATH)
    print("Press Ctrl+C to stop.")
    while True:
        data = parse_sta()
        if data is None:
            print("Waiting for %s..." % STA_PATH)
        else:
            progress = data["step_time"] / TOTAL_TIME
            print("%s %6.2f%% inc %d/%d time %.6g/%g" % (
                bar(progress),
                100.0 * progress,
                data["inc"],
                MAX_INC,
                data["step_time"],
                TOTAL_TIME,
            ))
            if data["step_time"] >= TOTAL_TIME:
                break
        time.sleep(10)


if __name__ == "__main__":
    main()
