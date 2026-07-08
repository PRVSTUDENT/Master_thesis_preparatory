#!/usr/bin/env bash
set -euo pipefail

CASE_DIR="${CASE_DIR:-/scratch/pr21vyci/git_work/Master_thesis_preparatory/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4q_long_adaptive_chain_1cpu}"
cd "$CASE_DIR"

{
  echo "created=$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "case_dir=$PWD"
  echo "classification_scope=feasibility_only_after_cycle1000_accuracy_fail"
  echo "R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1"
  echo "--- qstat -u pr21vyci ---"
  qstat -u pr21vyci || true
  echo "--- df -h /scratch9 /scratch /home ---"
  df -h /scratch9 /scratch /home 2>/dev/null || df -h /scratch /home || true
  echo "--- du -sh /scratch9/pr21vyci ---"
  du -sh /scratch9/pr21vyci 2>/dev/null || true
  echo "--- verify R4Q3 heavy source ---"
  ls -lh /scratch/pr21vyci/stage16n_r4q3_continue_from_cycle750_1cpu/1362636.mmaster02/stage16n_r4q3_block03_750_to_771_solve_772_to_1000.{sta,res,stt,mdl,prt,sim,odb}
} > R4Q_F_DEPENDENT_QUEUE_SUBMIT_GATE.txt

qstat -u pr21vyci > qstat_r4q_f_dependent_queue_before.txt || true

submit_one() {
  local label="$1"
  local dependency="$2"
  local script="$3"
  local receipt="R4Q_F_DEPENDENT_QUEUE_${label}_GUARDED_SUBMIT.txt"
  local out job_id
  if [[ -n "$dependency" ]]; then
    out=$(/home/pr21vyci/bin/qsub_abq_guarded -W "depend=afterok:${dependency}" "$script" 2>&1)
  else
    out=$(/home/pr21vyci/bin/qsub_abq_guarded "$script" 2>&1)
  fi
  printf '%s\n' "$out" > "$receipt"
  printf '%s\n' "$out" >&2
  job_id=$(printf '%s\n' "$out" | grep -Eo '[0-9]+\.mmaster02' | tail -n 1)
  if [[ -z "$job_id" ]]; then
    echo "Could not parse ${label} job id" >&2
    exit 3
  fi
  qstat -f "$job_id" > "qstat_${label,,}_${job_id%%.*}_after_submission.txt" || true
  echo "$job_id"
}

r4q4f="$(submit_one R4Q4F "" run_r4q4f_continue_from_cycle1000_1cpu.pbs)"
perl -0pi -e "s/R4Q4F_JOBID_PLACEHOLDER/$r4q4f/g" run_r4q5f_continue_from_cycle1250_1cpu.pbs

r4q5f="$(submit_one R4Q5F "$r4q4f" run_r4q5f_continue_from_cycle1250_1cpu.pbs)"
perl -0pi -e "s/R4Q5F_JOBID_PLACEHOLDER/$r4q5f/g" run_r4q6f_continue_from_cycle1500_1cpu.pbs

r4q6f="$(submit_one R4Q6F "$r4q5f" run_r4q6f_continue_from_cycle1500_1cpu.pbs)"
perl -0pi -e "s/R4Q6F_JOBID_PLACEHOLDER/$r4q6f/g" run_r4q7f_continue_from_cycle1750_1cpu.pbs

r4q7f="$(submit_one R4Q7F "$r4q6f" run_r4q7f_continue_from_cycle1750_1cpu.pbs)"

{
  echo "submitted_at=$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "classification_scope=feasibility_only_after_cycle1000_accuracy_fail"
  echo "R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1"
  echo "R4Q4F=$r4q4f dependency=none target=1000_to_1021_solve_1022_to_1250"
  echo "R4Q5F=$r4q5f dependency=afterok:$r4q4f target=1250_to_1271_solve_1272_to_1500"
  echo "R4Q6F=$r4q6f dependency=afterok:$r4q5f target=1500_to_1521_solve_1522_to_1750"
  echo "R4Q7F=$r4q7f dependency=afterok:$r4q6f target=1750_to_1771_solve_1772_to_2000"
} > R4Q_F_DEPENDENT_QUEUE_SUBMITTED_JOBS.txt

qstat -u pr21vyci > qstat_r4q_f_dependent_queue_after.txt || true
cat R4Q_F_DEPENDENT_QUEUE_SUBMITTED_JOBS.txt
