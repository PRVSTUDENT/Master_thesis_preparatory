from __future__ import print_function

import os
import time


JOB = "chaboche_vp_v1_cyclic_eps005_500cycles"
STA_PATH = JOB + ".sta"
TOTAL_TIME = 500.0


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


def progress_bar(value, total=TOTAL_TIME, width=40):
    if value is None:
        return "[" + "-" * width + "]"
    frac = max(0.0, min(1.0, value / total))
    done = int(round(frac * width))
    return "[" + "#" * done + "-" * (width - done) + "]"


def main():
    print("Monitoring %s" % STA_PATH)

    while True:
        data = parse_sta()

        if data is None:
            print("Waiting for %s..." % STA_PATH)
        else:
            pct = 100.0 * data["step_time"] / TOTAL_TIME
            print(
                "%s %6.2f%% | inc %d | step_time %.6f / %.1f"
                % (progress_bar(data["step_time"]), pct, data["inc"], data["step_time"], TOTAL_TIME)
            )

            if data["step_time"] >= TOTAL_TIME:
                break

        time.sleep(20)


if __name__ == "__main__":
    main()
