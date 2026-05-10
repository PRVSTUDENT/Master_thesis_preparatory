"""Quick diagnostic to list ODB step and frame information."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
odb_path = str(ROOT / 'chaboche_vp_v1_cyclic_eps005_20cycles.odb')

try:
    from odbAccess import openOdb
    print(f'Opening: {odb_path}')
    odb = openOdb(odb_path, readOnly=True)
    
    print(f'Available steps: {list(odb.steps.keys())}')
    
    for step_name, step in odb.steps.items():
        print(f'\n  Step: {step_name}')
        frames = step.frames
        print(f'    Number of frames: {len(frames)}')
        if frames:
            print(f'    First frame time: {frames[0].frameValue}')
            print(f'    Last frame time: {frames[-1].frameValue}')
            # Find frames near 19 and 20
            for t in [19.0, 20.0]:
                best = None
                best_err = float('inf')
                for f in frames:
                    err = abs(f.frameValue - t)
                    if err < best_err:
                        best_err = err
                        best = f
                if best:
                    print(f'    Nearest frame to {t}: {best.frameValue} (error={best_err})')
    
    odb.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
