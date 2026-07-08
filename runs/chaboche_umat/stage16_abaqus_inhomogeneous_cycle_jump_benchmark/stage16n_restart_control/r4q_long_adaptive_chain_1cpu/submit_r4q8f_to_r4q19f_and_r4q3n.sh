#!/usr/bin/env bash
set -euo pipefail

CASE_DIR="${CASE_DIR:-/scratch/pr21vyci/git_work/Master_thesis_preparatory/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4q_long_adaptive_chain_1cpu}"
cd "$CASE_DIR"

GATE_FILE="R4Q8F_TO_R4Q19F_SUBMIT_GATE.txt"
AUDIT_FILE="R4Q8F_TO_R4Q19F_SCRATCH9_SIZE_AUDIT.txt"
SUBMITTED_FILE="R4Q8F_TO_R4Q19F_SUBMITTED_JOBS.txt"
DIAG_FILE="R4Q3N_EXACT_NATIVE_SUBMISSION_STATUS.txt"
R4Q7F_DIR="/scratch/pr21vyci/stage16n_r4q7f_continue_from_cycle1750_1cpu/1363633.mmaster02"
R4Q7F_JOB="stage16n_r4q7f_block07_1750_to_1771_solve_1772_to_2000"
R4Q2_DIR="/scratch/pr21vyci/stage16n_r4q2_continue_from_cycle500_1cpu/1362597.mmaster02"
R4Q2_JOB="stage16n_r4q2_block02_500_to_521_solve_522_to_750"

{
  echo "created=$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "case_dir=$PWD"
  echo "classification_scope=feasibility_only_after_cycle1000_accuracy_fail"
  echo "R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1"
  echo "planned_chain=R4Q8F..R4Q19F"
  echo "stop_cycle=5000"
  echo "--- qstat -u pr21vyci ---"
  qstat -u pr21vyci || true
  echo "--- df -h /scratch9 /scratch /home ---"
  df -h /scratch9 /scratch /home 2>/dev/null || df -h /scratch /home || true
  echo "--- du -sh /scratch9/pr21vyci ---"
  du -sh /scratch9/pr21vyci 2>/dev/null || true
  echo "--- verify R4Q7F cycle2000 heavy source ---"
  ls -lh "$R4Q7F_DIR/$R4Q7F_JOB".{sta,res,stt,mdl,prt,sim,odb}
  echo "--- verify R4Q2 cycle750 heavy source for R4Q3N diagnostic ---"
  ls -lh "$R4Q2_DIR/$R4Q2_JOB".{sta,res,stt,mdl,prt,sim,odb}
} > "$GATE_FILE"

scratch9_tb=$(du -s /scratch9/pr21vyci 2>/dev/null | awk '{printf "%.3f", $1/1024/1024/1024}')
if awk "BEGIN {exit !($scratch9_tb > 5.0)}"; then
  {
    echo "created=$(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "scratch9_pr21vyci_T=${scratch9_tb}"
    echo "reason=/scratch9/pr21vyci exceeded 5T pre-submit audit threshold"
    echo "--- du -h --max-depth=1 /scratch9/pr21vyci | sort -hr | head -80 ---"
    du -h --max-depth=1 /scratch9/pr21vyci 2>/dev/null | sort -hr | head -80
  } > "$AUDIT_FILE"
else
  {
    echo "created=$(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "scratch9_pr21vyci_T=${scratch9_tb}"
    echo "audit_skipped=below_5T_threshold"
  } > "$AUDIT_FILE"
fi

qstat -u pr21vyci > qstat_r4q8f_to_r4q19f_before_submission.txt || true

submit_one() {
  local label="$1"
  local dependency="$2"
  local script="$3"
  local receipt="R4Q8F_TO_R4Q19F_${label}_GUARDED_SUBMIT.txt"
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

r4q8f="$(submit_one R4Q8F "" run_r4q8f_continue_from_cycle2000_1cpu.pbs)"
perl -0pi -e "s/R4Q8F_JOBID_PLACEHOLDER/$r4q8f/g" run_r4q9f_continue_from_cycle2250_1cpu.pbs
r4q9f="$(submit_one R4Q9F "$r4q8f" run_r4q9f_continue_from_cycle2250_1cpu.pbs)"
perl -0pi -e "s/R4Q9F_JOBID_PLACEHOLDER/$r4q9f/g" run_r4q10f_continue_from_cycle2500_1cpu.pbs
r4q10f="$(submit_one R4Q10F "$r4q9f" run_r4q10f_continue_from_cycle2500_1cpu.pbs)"
perl -0pi -e "s/R4Q10F_JOBID_PLACEHOLDER/$r4q10f/g" run_r4q11f_continue_from_cycle2750_1cpu.pbs
r4q11f="$(submit_one R4Q11F "$r4q10f" run_r4q11f_continue_from_cycle2750_1cpu.pbs)"
perl -0pi -e "s/R4Q11F_JOBID_PLACEHOLDER/$r4q11f/g" run_r4q12f_continue_from_cycle3000_1cpu.pbs
r4q12f="$(submit_one R4Q12F "$r4q11f" run_r4q12f_continue_from_cycle3000_1cpu.pbs)"
perl -0pi -e "s/R4Q12F_JOBID_PLACEHOLDER/$r4q12f/g" run_r4q13f_continue_from_cycle3250_1cpu.pbs
r4q13f="$(submit_one R4Q13F "$r4q12f" run_r4q13f_continue_from_cycle3250_1cpu.pbs)"
perl -0pi -e "s/R4Q13F_JOBID_PLACEHOLDER/$r4q13f/g" run_r4q14f_continue_from_cycle3500_1cpu.pbs
r4q14f="$(submit_one R4Q14F "$r4q13f" run_r4q14f_continue_from_cycle3500_1cpu.pbs)"
perl -0pi -e "s/R4Q14F_JOBID_PLACEHOLDER/$r4q14f/g" run_r4q15f_continue_from_cycle3750_1cpu.pbs
r4q15f="$(submit_one R4Q15F "$r4q14f" run_r4q15f_continue_from_cycle3750_1cpu.pbs)"
perl -0pi -e "s/R4Q15F_JOBID_PLACEHOLDER/$r4q15f/g" run_r4q16f_continue_from_cycle4000_1cpu.pbs
r4q16f="$(submit_one R4Q16F "$r4q15f" run_r4q16f_continue_from_cycle4000_1cpu.pbs)"
perl -0pi -e "s/R4Q16F_JOBID_PLACEHOLDER/$r4q16f/g" run_r4q17f_continue_from_cycle4250_1cpu.pbs
r4q17f="$(submit_one R4Q17F "$r4q16f" run_r4q17f_continue_from_cycle4250_1cpu.pbs)"
perl -0pi -e "s/R4Q17F_JOBID_PLACEHOLDER/$r4q17f/g" run_r4q18f_continue_from_cycle4500_1cpu.pbs
r4q18f="$(submit_one R4Q18F "$r4q17f" run_r4q18f_continue_from_cycle4500_1cpu.pbs)"
perl -0pi -e "s/R4Q18F_JOBID_PLACEHOLDER/$r4q18f/g" run_r4q19f_continue_from_cycle4750_1cpu.pbs
r4q19f="$(submit_one R4Q19F "$r4q18f" run_r4q19f_continue_from_cycle4750_1cpu.pbs)"

{
  echo "submitted_at=$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "classification_scope=feasibility_only_after_cycle1000_accuracy_fail"
  echo "R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1"
  echo "dependency_mode=strict_afterok"
  echo "stop_cycle=5000"
  echo "R4Q8F=$r4q8f dependency=none target=2000_to_2021_solve_2022_to_2250"
  echo "R4Q9F=$r4q9f dependency=afterok:$r4q8f target=2250_to_2271_solve_2272_to_2500"
  echo "R4Q10F=$r4q10f dependency=afterok:$r4q9f target=2500_to_2521_solve_2522_to_2750"
  echo "R4Q11F=$r4q11f dependency=afterok:$r4q10f target=2750_to_2771_solve_2772_to_3000"
  echo "R4Q12F=$r4q12f dependency=afterok:$r4q11f target=3000_to_3021_solve_3022_to_3250"
  echo "R4Q13F=$r4q13f dependency=afterok:$r4q12f target=3250_to_3271_solve_3272_to_3500"
  echo "R4Q14F=$r4q14f dependency=afterok:$r4q13f target=3500_to_3521_solve_3522_to_3750"
  echo "R4Q15F=$r4q15f dependency=afterok:$r4q14f target=3750_to_3771_solve_3772_to_4000"
  echo "R4Q16F=$r4q16f dependency=afterok:$r4q15f target=4000_to_4021_solve_4022_to_4250"
  echo "R4Q17F=$r4q17f dependency=afterok:$r4q16f target=4250_to_4271_solve_4272_to_4500"
  echo "R4Q18F=$r4q18f dependency=afterok:$r4q17f target=4500_to_4521_solve_4522_to_4750"
  echo "R4Q19F=$r4q19f dependency=afterok:$r4q18f target=4750_to_4771_solve_4772_to_5000"
} > "$SUBMITTED_FILE"

qstat -u pr21vyci > qstat_r4q8f_to_r4q19f_after_submission.txt || true

running_stage16n=$(qstat -u pr21vyci 2>/dev/null | awk 'NR > 5 && $4 ~ /stage16n/ && $10 == "R" {count++} END {print count+0}')
if [[ "$running_stage16n" -lt 2 ]]; then
  diag_out=$(/home/pr21vyci/bin/qsub_abq_guarded run_r4q3n_exact_native_control_750_to_1000_1cpu.pbs 2>&1)
  printf '%s\n' "$diag_out" > R4Q3N_EXACT_NATIVE_GUARDED_SUBMIT.txt
  diag_job=$(printf '%s\n' "$diag_out" | grep -Eo '[0-9]+\.mmaster02' | tail -n 1)
  if [[ -z "$diag_job" ]]; then
    echo "diagnostic_submit_status=parse_failed" > "$DIAG_FILE"
    echo "$diag_out" >> "$DIAG_FILE"
    exit 4
  fi
  qstat -f "$diag_job" > "qstat_r4q3n_${diag_job%%.*}_after_submission.txt" || true
  {
    echo "submitted_at=$(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "diagnostic_submit_status=submitted"
    echo "running_stage16n_before_diagnostic=$running_stage16n"
    echo "R4Q3N_exact_native_control_750_to_1000=$diag_job"
    echo "purpose=exact_native_control_from_R4Q2_cycle750_to_cycle1000_without_750_to_771_extrapolated_overwrite"
  } > "$DIAG_FILE"
else
  {
    echo "submitted_at=$(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "diagnostic_submit_status=skipped_two_job_limit"
    echo "running_stage16n_before_diagnostic=$running_stage16n"
  } > "$DIAG_FILE"
fi

qstat -u pr21vyci > qstat_r4q8f_to_r4q19f_plus_r4q3n_after_submission.txt || true
cat "$SUBMITTED_FILE"
cat "$DIAG_FILE"
