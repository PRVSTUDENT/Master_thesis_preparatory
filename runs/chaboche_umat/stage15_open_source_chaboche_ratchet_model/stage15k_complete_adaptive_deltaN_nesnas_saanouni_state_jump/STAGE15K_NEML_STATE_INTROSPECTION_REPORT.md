# Stage 15K NEML State Introspection Report

## Execution Context Note
- Local Windows/current environment pre-check: **NEML unavailable** (`ModuleNotFoundError: No module named 'neml'`).
- HPC environment result: see the current run details below.

## Environment
- Python executable: `/cluster/stages/2024.0/spack-0.22/opt/spack/linux-rocky8-cascadelake/gcc-11.4.0/python-3.11.7-qfpdtq2pisspwunkuc4fqloxqo2ltw6j/bin/python`
- Python version: `3.11.7 (main, Jul 24 2024, 09:40:09) [GCC 11.4.0]`
- Platform: `Linux-4.18.0-553.124.1.el8_10.x86_64-x86_64-with-glibc2.28`
- Working directory: `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump`

## NEML Import
- Status: **PASS**
- NEML path: `/home/pr21vyci/.local/lib/python3.11/site-packages/neml/__init__.py`
- NumPy version: `2.4.4`

## Model Construction
- Status: **PASS**
- Model type: `SmallStrainRateIndependentPlasticity`
- Model module: `neml.models`

## Available Model Methods
- `RJ`
- `alpha`
- `elastic_strains`
- `get_damage`
- `init_hist`
- `init_store`
- `init_x`
- `initial_history`
- `is_damage_model`
- `make_trial_state`
- `populate_hist`
- `prefix`
- `report_internal_variable_names`
- `save`
- `serialize`
- `set_elastic_model`
- `should_del_element`
- `update_ld_inc`
- `update_sd`

## Model Update/Internal-State Candidate Methods
- `init_hist`: `signature unavailable: ValueError: no signature found for builtin <built-in method init_hist of PyCapsule object at 0x14cb9fd800c0>`
- `init_store`: `signature unavailable: ValueError: no signature found for builtin <built-in method init_store of PyCapsule object at 0x14cb9fd80150>`
- `initial_history`: `signature unavailable: ValueError: no signature found for builtin <built-in method initial_history of PyCapsule object at 0x14cb9fd801b0>`
- `populate_hist`: `signature unavailable: ValueError: no signature found for builtin <built-in method populate_hist of PyCapsule object at 0x14cb9fd80060>`
- `report_internal_variable_names`: `signature unavailable: ValueError: no signature found for builtin <built-in method report_internal_variable_names of PyCapsule object at 0x14cb0e6fae20>`
- `update_ld_inc`: `signature unavailable: ValueError: no signature found for builtin <built-in method update_ld_inc of PyCapsule object at 0x14cb0e6faee0>`
- `update_sd`: `signature unavailable: ValueError: no signature found for builtin <built-in method update_sd of PyCapsule object at 0x14cb0e6fae80>`

## Model State Metadata
- `report_internal_variable_names()` status: **PASS**
- Internal variable count: `25`
- Internal variable names: `small_stress_0, small_stress_1, small_stress_2, small_stress_3, small_stress_4, small_stress_5, alpha, backstress_0_0, backstress_0_1, backstress_0_2, backstress_0_3, backstress_0_4, backstress_0_5, backstress_1_0, backstress_1_1, backstress_1_2, backstress_1_3, backstress_1_4, backstress_1_5, backstress_2_0, backstress_2_1, backstress_2_2, backstress_2_3, backstress_2_4, backstress_2_5`
- `init_store()` status: **PASS**
- Initial history type: `ndarray`
- Initial history length: `25`
- Initial history preview: `array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0.])`

## Available Driver Methods
### `neml.drivers` module callables
- `Driver`
- `Driver_sd`
- `MaximumIterations`
- `MaximumSubdivisions`
- `classify`
- `creep`
- `def_grad_driver`
- `isochronous_curve`
- `leggauss`
- `newton`
- `offset_stress`
- `rate_jump_test`
- `scalar_newton`
- `skew`
- `strain_cyclic`
- `strain_cyclic_extrapolated`
- `strain_cyclic_followup`
- `stress_cyclic`
- `stress_relaxation`
- `sym`
- `thermomechanical_strain_raw`
- `uniaxial_test`

### `drivers.Driver_sd` instance methods
- `erate_einc_step`
- `erate_step`
- `solve_try`
- `srate_sinc_step`
- `strain_hold_step`
- `strain_step`
- `stress_step`
- `update_thermal_strain`

## Driver Data Attributes
- `T`: type `ndarray`, len `1`, preview `array([293.15])`
- `T_int`: type `list`, len `1`, preview `[293.15]`
- `atol`: type `float`, len `None`, preview `1e-10`
- `history`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0., 0., 0.]])`
- `mechanical_strain`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0.]])`
- `mechanical_strain_int`: type `list`, len `1`, preview `[array([0., 0., 0., 0., 0., 0.])]`
- `miter`: type `int`, len `None`, preview `25`
- `model`: type `SmallStrainRateIndependentPlasticity`, len `None`, preview `<neml.models.SmallStrainRateIndependentPlasticity object at 0x14cb145b7b30>`
- `nts`: type `bool`, len `None`, preview `False`
- `p`: type `ndarray`, len `1`, preview `array([0.])`
- `p_int`: type `list`, len `1`, preview `[0.0]`
- `rtol`: type `float`, len `None`, preview `1e-06`
- `stored`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0., 0., 0.]])`
- `stored_int`: type `list`, len `1`, preview `[array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0.])]`
- `strain`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0.]])`
- `strain_int`: type `list`, len `1`, preview `[array([0., 0., 0., 0., 0., 0.])]`
- `stress`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0.]])`
- `stress_int`: type `list`, len `1`, preview `[array([0., 0., 0., 0., 0., 0.])]`
- `t`: type `ndarray`, len `1`, preview `array([0.])`
- `t_int`: type `list`, len `1`, preview `[0.0]`
- `thermal_strain`: type `ndarray`, len `1`, preview `array([[0., 0., 0., 0., 0., 0.]])`
- `thermal_strain_int`: type `list`, len `1`, preview `[array([0., 0., 0., 0., 0., 0.])]`
- `u`: type `ndarray`, len `1`, preview `array([0.])`
- `u_int`: type `list`, len `1`, preview `[0.0]`
- `verbose`: type `bool`, len `None`, preview `False`

## Stress, Strain, And History Storage
- `p_int`: type `list`, len `2`, preview `[0.0, 0.015217548138424098]`
- `stored_int`: type `list`, len `2`, preview `[array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0.]), array([ 0.00000000e+...`
- `strain_int`: type `list`, len `2`, preview `[array([0., 0., 0., 0., 0., 0.]), array([ 0.00085363, -0.00030681, -0.00030681,  0.        ,  0.        ,
        0.        ])]`
- `stress_int`: type `list`, len `2`, preview `[array([0., 0., 0., 0., 0., 0.]), array([1.19999998e+02, 8.65656118e-07, 8.65656120e-07, 0.00000000e+00,
       0.00000000e+00, 0.0000000...`
- `t_int`: type `list`, len `2`, preview `[0.0, np.float64(1200000.0)]`
- `u_int`: type `list`, len `2`, preview `[0.0, 0.05121754678800056]`
- Interpretation: the public driver stores path history in list-like attributes such as `stress_int`, `strain_int`, `stored_int`, and `t_int` when present.

## Lower-Level Model Update Access
- `update_sd` available: `True`
- `init_store` available: `True`
- Probe attempted: `True`
- Probe passed: `True`
- Probe message: `direct update_sd can be called with explicit prior state`
- Explicit state fields implied by `update_sd`: `strain, stress, history, temperature, time, u, p`
- Max absolute repeat difference: `0.0`

## Full State Save/Restore Assessment
- Driver exposes stress/strain/history/time storage: `True`
- Lower-level explicit state update is accessible: `True`
- Assessment: **PASS**. Full constitutive state appears representable as strain, stress, history/internal variables, temperature, time, energy `u`, and dissipation/plastic work `p`, and `update_sd` accepts those as explicit prior-state inputs.
- Required next step: run the Stage 15K restart/reinjection test and require near-roundoff differences before any state jumping.

## Stop/Go Decision
**GO TO RESTART TEST ONLY.** Do not proceed to fixed/adaptive jumps until restart/reinjection passes with near-roundoff differences.
