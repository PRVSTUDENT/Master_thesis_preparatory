# File Inventory

This file records what each tracked file in the organized repository is for.

## Docs

- `docs/abaqus_one_cycle_model_setup.md` - walkthrough of the one-cycle Abaqus model setup.
- `docs/cycle_jump_worklog.md` - work log for cycle-jump experiments and decisions.
- `docs/doi_links.md` - reference list of DOI links used during the thesis work.
- `docs/reports/ansys_workbench_check.txt` - notes from checking behavior in Ansys Workbench.
- `docs/reports/ep_cycle_jump_accumulated.txt` - cycle-jump notes for the accumulated EP workflow.
- `docs/reports/ep_cycle_jump_adaptive.txt` - cycle-jump notes for the adaptive EP workflow.
- `docs/reports/ep_cycle_jump_demo.txt` - demo notes for the 1D EP cycle-jump workflow.
- `docs/reports/IguanaTex_tmp.aux` - temporary LaTeX auxiliary file from a figure export.
- `docs/reports/IguanaTex_tmp.dvi` - temporary LaTeX DVI file from a figure export.
- `docs/reports/IguanaTex_tmp.log` - temporary LaTeX log file from a figure export.
- `docs/reports/IguanaTex_tmp.tex` - temporary LaTeX source used for the IguanaTex export.
- `docs/reports/miner_block_results.txt` - summary of the miner block result run.
- `docs/reports/miner_variable_blocks_results.txt` - summary of the variable-block miner run.

## Scripts

### Abaqus replay

- `scripts/abaqus/abaqus.rpy` - main Abaqus/CAE replay script for the one-cycle model state.
- `scripts/abaqus/abaqus.rpy.2` - earlier replay snapshot.
- `scripts/abaqus/abaqus.rpy.3` - earlier replay snapshot.
- `scripts/abaqus/abaqus.rpy.4` - earlier replay snapshot.
- `scripts/abaqus/abaqus.rpy.5` - earlier replay snapshot.
- `scripts/abaqus/abaqus.rpy.13` - later replay snapshot.
- `scripts/abaqus/abaqus.rpy.14` - later replay snapshot.
- `scripts/abaqus/abaqus.rpy.15` - later replay snapshot.
- `scripts/abaqus/abaqus.rpy.16` - later replay snapshot.

### Preprocessing and model scripts

- `scripts/steps/step1_extract_stress_range_NOSET.py` - extracts stress range without relying on named sets.
- `scripts/steps/step2_linear_elastic_miner_block.py` - builds the linear elastic miner-block model.
- `scripts/steps/step3_linear_elastic_variable_blocks_noprint.py` - variable-block elastic script with reduced console noise.
- `scripts/steps/step_ep1_1D_ep_cycle_jump_demo.py` - demo script for 1D elastic-plastic cycle jumping.
- `scripts/steps/step_ep2_adaptive_cycle_jump_ep_1D.py` - adaptive 1D EP cycle-jump implementation.
- `scripts/steps/step_ep3_cycle_jump_accumulated_ep_1D.py` - accumulated 1D EP cycle-jump implementation.
- `scripts/steps/step_vp1_cycle_averaged_jump_1D.py` - cycle-averaged jump script.
- `scripts/steps/step_vp2_implicit_cycle_jump_1D.py` - implicit cycle-jump controller script.
- `scripts/steps/step_vp3_controller_autogrow.py` - controller/autogrowth helper.

### Post-processing and verification

- `scripts/postprocessing/extract_fd.py` - extracts force-displacement data from `mono_ep_test_fix.odb` and writes CSV/PNG outputs.
- `scripts/vp/vp_allpd__10cycles8.py` - all plastic dissipation workflow for the 10-cycle 8 variant.
- `scripts/vp/vp_odb_extract_allpd_per_cycle.py` - extracts all plastic dissipation per cycle from an ODB.
- `scripts/vp/vp_odb_extract_eqp_per_cycle.py` - extracts equivalent plastic strain per cycle.
- `scripts/vp/vp_odb_extract_eqp_per_cycle_SCANFRAMES.py` - scans frames to extract equivalent plastic strain.
- `scripts/vp/vp_odb_extract_peeq_per_cycle.py` - extracts PEEQ per cycle from an ODB.
- `scripts/vp/vp_odb_extract_peeq_per_cycle__10cycles7.py` - PEEQ extraction for the 10-cycle 7 variant.
- `scripts/vp/vp_peeq__10cycles8.py` - PEEQ workflow for the 10-cycle 8 variant.
- `scripts/vp/vp_sanity_check_loading_and_plasticity.py` - sanity check for loading and plasticity behavior.
- `scripts/vp/vp_sanity__10cycles8.py` - sanity check script for the 10-cycle 8 workflow.

## Models

- `models/one_cycle/one_cycle.jnl` - Abaqus journal file for recreating the one-cycle CAE session state.

## Runs

### mono_ep_test

- `runs/mono_ep_test/mono_ep_test.inp` - corrected input deck for the mono-ep test.
- `runs/mono_ep_test/mono_ep_test.odb` - ODB for the mono-ep test.
- `runs/mono_ep_test/mono_ep_test_fix.odb` - corrected ODB used for force-displacement extraction.
- `runs/mono_ep_test/*.com`, `.dat`, `.ipm`, `.log`, `.msg`, `.prt`, `.sta` - solver submission and status files for the mono-ep test jobs.

### one_cycle

- `runs/one_cycle/one-cycle.inp` - one-cycle analysis input deck.
- `runs/one_cycle/one-cycle.odb` - one-cycle analysis database.
- `runs/one_cycle/*.com`, `.dat`, `.ipm`, `.log`, `.msg`, `.prt`, `.sta` - solver submission and status files for the one-cycle analysis.

### vp_10cycles

- `runs/vp_10cycles/vp_10cycles*.inp` - input decks for the 10-cycle variants.
- `runs/vp_10cycles/vp_10cycles*.odb` - output databases for the 10-cycle variants.
- `runs/vp_10cycles/vp_10cycles*.com`, `.dat`, `.env`, `.ipm`, `.log`, `.msg`, `.prt`, `.sta`, `.odb_f` - solver and helper files for the 10-cycle variants.

## Analysis outputs

- `analysis/force_displacement.csv` - force-displacement data extracted from `mono_ep_test_fix.odb`.
- `analysis/force_displacement.png` - force-displacement plot extracted from `mono_ep_test_fix.odb`.
- `analysis/one_cycle_S11_minmax_NOSET.csv` - stress extrema data for the one-cycle stress range run.
- `analysis/vp_cycle_end_eqpmax.csv` - end-of-cycle equivalent plastic strain maxima.
- `analysis/vp_cycle_end_peeqmax.csv` - end-of-cycle PEEQ maxima.
- `analysis/vp_cycle_inc_allpd.csv` - incremental all-plastic-dissipation results.
- `analysis/vp_cycle_inc_deqp.csv` - incremental equivalent plastic strain results.
- `analysis/vp_cycle_inc_dpeeq.csv` - incremental PEEQ results.
- `analysis/vp_cycle_jump_avg.txt` - average cycle-jump log/output.
- `analysis/vp_cycle_jump_controller.txt` - controller log/output for cycle jumping.
- `analysis/vp_cycle_jump_implicit.txt` - implicit cycle-jump log/output.
- `analysis/vp_field_choice.txt` - notes on field choice used in extraction.
- `analysis/vp_history_keys.txt` - history key inventory from ODB inspection.
- `analysis/vp_odb_field_keys.txt` - field key inventory from ODB inspection.
- `analysis/vp_sanity_report.txt` - sanity report for the VP workflow.
- `analysis/vp_frames_eqpmax.csv` - frame-based equivalent plastic strain maxima.
- `analysis/vp_frames_peeqmax.csv` - frame-based PEEQ maxima.
- `analysis/ep_cycle_jump_accumulated.txt` - accumulated EP cycle-jump notes.
- `analysis/ep_cycle_jump_adaptive.txt` - adaptive EP cycle-jump notes.
- `analysis/ep_cycle_jump_demo.txt` - demo EP cycle-jump notes.
- `analysis/ansys_workbench_check.txt` - comparison note from Ansys Workbench.
- `analysis/miner_block_results.txt` - miner block summary results.
- `analysis/miner_variable_blocks_results.txt` - variable-block miner summary results.

## Raw archive still in `one_cycle_run/`

These files were left in `one_cycle_run/` because they were locked or part of the active raw archive during reorganization:

- `one_cycle_run/abaqus.rpy`
- `one_cycle_run/abaqus_acis.log`
- `one_cycle_run/abq.app_cache`
- `one_cycle_run/dsm_cache/`
- `one_cycle_run/ffmpeg-2023-09-04-git-f8503b4c33-full_build/`
- `one_cycle_run/mono_ep_test.odb`
- `one_cycle_run/mono_ep_test_fix.odb`
- `one_cycle_run/one_cycle.cae`
- `one_cycle_run/one_cycle.rec`
