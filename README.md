# Master_thesis_preparatory

Repository for Abaqus-based master thesis preparation, including model setup notes, replay scripts, input files, solver runs, and post-processing outputs.

## Layout

- `docs/` - project notes, work logs, reference links, and this repository inventory
- `scripts/` - Abaqus replay scripts, model-building scripts, and post-processing scripts
- `models/` - CAE/journal artifacts that define reusable model state
- `runs/` - job input decks and solver output files grouped by analysis case
- `analysis/` - extracted CSV data, plots, and result summaries
- `one_cycle_run/` - raw archive folder that still contains a few locked or in-use Abaqus artifacts

## Typical workflow

1. Run an Abaqus job from the relevant `runs/` folder, for example:

   ```powershell
   Set-Location 'D:\TUBAF\Master_Thesis\Abaqus_trial\runs\mono_ep_test'
   abaqus job=mono_ep_test_fix input=mono_ep_test.inp interactive
   ```

2. Extract force-displacement data from the resulting ODB:

   ```powershell
   Set-Location 'D:\TUBAF\Master_Thesis\Abaqus_trial'
   abaqus python scripts\postprocessing\extract_fd.py
   ```

3. Review the outputs in `analysis/`.

## Notes

- The repository keeps both the Abaqus input decks and the generated outputs so the thesis workflow is reproducible.
- Some files in `one_cycle_run/` remain there because they were locked by another process during reorganization. They are still part of the repository and documented in `docs/file_inventory.md`.
