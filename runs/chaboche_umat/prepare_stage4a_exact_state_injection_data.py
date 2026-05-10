"""
prepare_stage4a_exact_state_injection_data.py

Stage 4A.1: Complete exact-state injection data extraction.

Behavior:
- If run inside Abaqus Python (odbAccess available), extracts STATEV(1..15) and
  stresses from the ODB at nearest frame to time=19.0 and time=20.0.
- Falls back to CSV extraction if odbAccess is unavailable.

Outputs (in `stage4_injected_cycle_jump/`):
- cycle19_exact_statev_for_injection.csv
- cycle19_exact_stress_for_injection.csv
- cycle20_reference_statev.csv
- cycle20_reference_stress.csv

This script does NOT run Abaqus, does NOT modify UMAT or input decks.
"""

from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parent
SRC_CSV = ROOT / 'chaboche_v1_full_statev_cycle_history.csv'
OUT_DIR = ROOT / 'stage4_injected_cycle_jump'
OUT_DIR.mkdir(exist_ok=True)


def extract_from_odb_odbaccess():
    """Extract cycle-19 and cycle-20 state/stress from ODB using odbAccess."""
    try:
        from odbAccess import openOdb  # type: ignore
    except ImportError:
        return None, None, None, None

    odb_path = str(ROOT / 'chaboche_vp_v1_cyclic_eps005_20cycles.odb')
    if not Path(odb_path).exists():
        print(f'ODB not found: {odb_path}')
        return None, None, None, None

    print(f'Opening ODB: {odb_path}')
    try:
        odb = openOdb(odb_path, readOnly=True)
    except Exception as e:
        print(f'Failed to open ODB: {e}')
        return None, None, None, None

    results = {}
    # Find the first step (typically the only step)
    step_name = list(odb.steps.keys())[0]
    print(f'Using step: {step_name}')
    
    for target_time in [19.0, 20.0]:
        frame_key = int(target_time)
        try:
            # Find nearest frame to target_time
            frames = odb.steps[step_name].frames
            best_frame = None
            best_error = float('inf')
            for frame in frames:
                error = abs(frame.frameValue - target_time)
                if error < best_error:
                    best_error = error
                    best_frame = frame
                if error < 1e-6:
                    break

            if best_frame is None:
                print(f'No frame found near time {target_time}')
                continue

            frame_time = best_frame.frameValue
            print(f'Target {target_time}: found frame at time {frame_time}, error={best_error}')

            # Extract SDV and stress
            frame_outputs = best_frame.fieldOutputs
            available_fields = list(frame_outputs.keys())
            
            sdv_dict = {}
            stress_dict = {}

            # SDV fields are individual (SDV1, SDV2, ..., SDV15)
            for i in range(1, 16):
                field_name = f'SDV{i}'
                if field_name in available_fields:
                    sdv_field = frame_outputs[field_name]
                    vals = []
                    try:
                        for val in sdv_field.values:
                            try:
                                data = val.data
                                # Each SDV field value is a scalar
                                vals.append(data)
                            except Exception:
                                pass
                        if vals:
                            sdv_dict[f'STATEV{i}_end'] = sum(vals) / len(vals)
                    except Exception as e:
                        pass

            # Stress field is common (S)
            if 'S' in available_fields:
                s_field = frame_outputs['S']
                stress_comps = {'S11': [], 'S22': [], 'S33': [], 'S12': [], 'S13': [], 'S23': []}
                try:
                    for val in s_field.values:
                        try:
                            data = val.data
                            # Stress tensor is [S11, S22, S33, S12, S13, S23]
                            if len(data) >= 6:
                                stress_comps['S11'].append(data[0])
                                stress_comps['S22'].append(data[1])
                                stress_comps['S33'].append(data[2])
                                stress_comps['S12'].append(data[3])
                                stress_comps['S13'].append(data[4])
                                stress_comps['S23'].append(data[5])
                        except Exception:
                            pass

                    for comp, vals in stress_comps.items():
                        if vals:
                            stress_dict[comp] = sum(vals) / len(vals)
                except Exception as e:
                    print(f'    Warning: Failed to extract stress: {e}')

            results[frame_key] = {
                'frame_time': frame_time,
                'time_error': best_error,
                'statev': sdv_dict,
                'stress': stress_dict,
            }

        except Exception as e:
            print(f'Error extracting time {target_time}: {e}')

    try:
        odb.close()
    except Exception:
        pass

    if 19 in results and 20 in results:
        return results[19], results[20], True, results
    return None, None, False, results


def read_from_history_csv(cycle_target=19):
    """Fallback: read from precomputed CSV."""
    if not SRC_CSV.exists():
        raise FileNotFoundError(f"Fallback CSV not found: {SRC_CSV}")
    with SRC_CSV.open('r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cycle = int(float(row['cycle']))
            except Exception:
                continue
            if cycle == cycle_target:
                statev = {}
                for i in range(1, 16):
                    key = f'STATEV{i}_end'
                    statev[key] = row.get(key, '')
                return {'statev': statev, 'stress': {}}
    raise RuntimeError(f'Cycle {cycle_target} not found in {SRC_CSV}')


def write_statev_csv(statev_dict, outpath):
    """Write STATEV to CSV."""
    keys = sorted(statev_dict.keys(), key=lambda s: int(''.join(filter(str.isdigit, s))))
    with open(outpath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['variable', 'value'])
        for k in keys:
            v = statev_dict.get(k, '')
            writer.writerow([k, v])


def write_stress_csv(stress_dict, outpath):
    """Write stress to CSV."""
    with open(outpath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['component', 'value'])
        for comp in ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']:
            v = stress_dict.get(comp, '')
            writer.writerow([comp, v])


def main():
    print('Stage 4A.1: Complete exact-state extraction')
    print('=' * 60)

    # Try ODB extraction
    result19_odb, result20_odb, odb_success, all_results = extract_from_odb_odbaccess()

    if odb_success:
        print('Successfully extracted from ODB')
        statev19 = result19_odb['statev']
        stress19 = result19_odb['stress']
        statev20 = result20_odb['statev']
        stress20 = result20_odb['stress']
        extracted_from = 'ODB (Abaqus Python)'
    else:
        print('ODB extraction failed or odbAccess unavailable; using fallback CSV')
        r19 = read_from_history_csv(19)
        r20 = read_from_history_csv(20)
        statev19 = r19['statev']
        stress19 = r19['stress']
        statev20 = r20['statev']
        stress20 = r20['stress']
        extracted_from = f'CSV fallback ({SRC_CSV})'

    # Write output files
    write_statev_csv(statev19, OUT_DIR / 'cycle19_exact_statev_for_injection.csv')
    write_stress_csv(stress19, OUT_DIR / 'cycle19_exact_stress_for_injection.csv')
    write_statev_csv(statev20, OUT_DIR / 'cycle20_reference_statev.csv')
    write_stress_csv(stress20, OUT_DIR / 'cycle20_reference_stress.csv')

    # Write report
    summary = OUT_DIR / 'STAGE4A_EXACT_STATE_INJECTION_PREP_REPORT.md'
    with summary.open('w') as f:
        f.write('# Stage 4A.1 — Exact-State Injection Preparation Report\n\n')
        f.write('Prepared: May 9, 2026\n\n')
        f.write('## Purpose\n')
        f.write('Extract exact cycle-19 STATEV and stress for injection-mechanics validation.\n\n')
        f.write('## Data source\n')
        f.write(f'Extracted from: {extracted_from}\n\n')
        f.write('## Files created\n')
        f.write('- cycle19_exact_statev_for_injection.csv\n')
        f.write('- cycle19_exact_stress_for_injection.csv\n')
        f.write('- cycle20_reference_statev.csv\n')
        f.write('- cycle20_reference_stress.csv\n\n')
        f.write('## Summary\n')
        if odb_success:
            f.write(f'Cycle-19 frame time: {result19_odb["frame_time"]:.6f}\n')
            f.write(f'Cycle-19 time error: {result19_odb["time_error"]:.6e}\n')
            f.write(f'Cycle-20 frame time: {result20_odb["frame_time"]:.6f}\n')
            f.write(f'Cycle-20 time error: {result20_odb["time_error"]:.6e}\n\n')
        f.write('| Variable | Cycle 19 | Cycle 20 |\n')
        f.write('|---:|---:|---:|\n')
        for i in range(1, 16):
            k = f'STATEV{i}_end'
            v19 = statev19.get(k, '')
            v20 = statev20.get(k, '')
            f.write(f'| {k} | {v19} | {v20} |\n')

        if stress19:
            f.write('\n| Stress | Cycle 19 | Cycle 20 |\n')
            f.write('|---:|---:|---:|\n')
            for comp in ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']:
                s19 = stress19.get(comp, '')
                s20 = stress20.get(comp, '')
                f.write(f'| {comp} | {s19} | {s20} |\n')

    print(f'\nFiles written to: {OUT_DIR}')
    print('Stage 4A.1 complete.')


if __name__ == '__main__':
    main()
