from __future__ import print_function

import os
import time


JOB = "chaboche_stage5b_predicted_cycle19_to_cycle20"
STA_PATH = JOB + ".sta"
TOTAL_TIME = 1.0
MAX_INC = 1000


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
                        "raw": line.rstrip(),
                    }
                except Exception:
                    pass
    return last


def bar(progress, width=40):
    filled = int(max(0.0, min(1.0, progress)) * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main():
    print("Monitoring %s.sta" % JOB)
    print("Press Ctrl+C to stop.")
    while True:
        data = parse_sta()
        if data is None:
            print("Waiting for %s..." % STA_PATH)
        else:
            progress = data["step_time"] / TOTAL_TIME if TOTAL_TIME else 0.0
            print("%s %6.2f%% inc %d/%d time %.6g" % (
                bar(progress),
                100.0 * progress,
                data["inc"],
                MAX_INC,
                data["step_time"],
            ))
            if data["step_time"] >= TOTAL_TIME:
                break
        time.sleep(5)


if __name__ == "__main__":
    main()
