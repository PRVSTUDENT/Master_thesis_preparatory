#!/bin/bash
set -euo pipefail

mkdir -p logs restart_verification

python stage15k_restart_reinjection_test.py 2>&1 | tee logs/stage15k_restart_reinjection_HPC.log
