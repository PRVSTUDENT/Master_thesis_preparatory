from __future__ import print_function

import os
import time


JOB = "chaboche_vp_v1_cyclic_eps005_100cycles"
STA_PATH = JOB + ".sta"


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
                        "attempts": int(parts[2]),
                        "step_time": float(parts[6]),
                    }
                except Exception:
                    pass
    return last


def progress_bar(value, total=100.0, width=30):
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
            pct = 100.0 * data["step_time"] / 100.0
            print(
                "%s %6.2f%% | inc %d | step_time %.6f / 100.0"
                % (progress_bar(data["step_time"]), pct, data["inc"], data["step_time"])
            )

            if data["step_time"] >= 100.0:
                break

        time.sleep(10)


if __name__ == "__main__":
    main()
