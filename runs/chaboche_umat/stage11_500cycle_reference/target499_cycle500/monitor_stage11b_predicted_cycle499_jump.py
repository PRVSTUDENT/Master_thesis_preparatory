from __future__ import print_function

import os
import time


JOB = "chaboche_stage11b_predicted_cycle499_to_cycle500"
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
                    last = {"inc": int(parts[1]), "step_time": float(parts[6])}
                except Exception:
                    pass
    return last


def main():
    print("Monitoring %s" % STA_PATH)
    while True:
        data = parse_sta()
        if data is None:
            print("Waiting for %s..." % STA_PATH)
        else:
            print("inc %d step_time %.8g" % (data["inc"], data["step_time"]))
            if data["step_time"] >= 1.0:
                break
        time.sleep(5)


if __name__ == "__main__":
    main()
