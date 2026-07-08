"""Check what fields are available in ODB."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
odb_path = str(ROOT / 'chaboche_vp_v1_cyclic_eps005_20cycles.odb')

try:
    from odbAccess import openOdb
    print(f'Opening: {odb_path}')
    odb = openOdb(odb_path, readOnly=True)
    
    step = odb.steps['CYCLIC_20']
    frames = step.frames
    
    if frames:
        frame = frames[-1]  # Last frame
        print(f'\nFrame time: {frame.frameValue}')
        print(f'Available fields:')
        for fname in sorted(frame.fieldOutputs.keys()):
            print(f'  - {fname}')
    
    odb.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
