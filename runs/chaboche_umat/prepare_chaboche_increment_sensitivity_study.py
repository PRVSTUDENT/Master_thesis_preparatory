#!/usr/bin/env python
"""
Prepare Chaboche-v1 increment-schedule sensitivity study input decks.

Purpose:
  Before attempting STATEV injection or full Nesnas-Saanouni-style restart
  continuation, quantify how sensitive the Chaboche-v1 UMAT integration is to
  the accepted time increment schedule.

Background:
  The exact-output diagnostic run used TIME MARKS=YES to force exact cycle-end
  output frames. This altered the accepted increment sequence, resulting in a
  5.12232% difference in cycle-20 STATEV(1) compared to the original baseline.
  This sensitivity study will isolate the effect of time increment size.

Procedure:
  1. Copy the original validated 20-cycle input deck.
  2. Create variants with controlled maximum time increment (DMAX) values.
  3. Document what was changed in each deck.
  4. Generate a study plan listing all decks and intended run commands.
  5. Do NOT run Abaqus automatically; only prepare input decks for manual runs.

Generated decks:
  - chaboche_eps005_20cycles_dt_original_output.inp
    Original 20-cycle deck with original output settings.
    DMAX = 0.02 (original)
    TIME MARKS = not used (original)

  - chaboche_eps005_20cycles_dtmax_0p02.inp
    Based on original; explicitly labeled DMAX=0.02.
    DMAX = 0.02 (same as original)
    TIME MARKS = not used
    Baseline for comparison.

  - chaboche_eps005_20cycles_dtmax_0p01.inp
    Based on original; reduced DMAX to force finer increments.
    DMAX = 0.01 (half of original)
    TIME MARKS = not used
    Should show effect of finer integration.

  - chaboche_eps005_20cycles_dtmax_0p005.inp
    Based on original; further reduced DMAX.
    DMAX = 0.005 (quarter of original)
    TIME MARKS = not used
    Should show effect of very fine integration.

  - chaboche_eps005_20cycles_exact_timemarks_diagnostic.inp
    Based on exact-output deck with TIME MARKS=YES.
    DMAX = 0.02 (same as original)
    TIME MARKS = YES
    Replicates the diagnostic branch for reference.
"""

import os
import shutil
import re
from pathlib import Path

def copy_and_modify_deck(source_file, dest_file, dmax_new=None, time_marks=False, comment=""):
    """
    Copy an input deck and optionally modify the DMAX parameter and TIME MARKS.
    
    Parameters:
      source_file: path to source .inp file
      dest_file: path to destination .inp file
      dmax_new: new DMAX value (float), or None to keep original
      time_marks: whether to add TIME MARKS=YES to OUTPUT statements
      comment: descriptive comment to add to file header
    
    Returns:
      A dictionary with change summary.
    """
    
    with open(source_file, 'r') as f:
        content = f.read()
    
    changes = {
        'source': source_file,
        'dest': dest_file,
        'dmax_changed': False,
        'dmax_old': None,
        'dmax_new': None,
        'time_marks_added': False,
        'warnings': []
    }
    
    # Find and modify DMAX in *STATIC line
    if dmax_new is not None:
        # Pattern: *STATIC\n<DINIT>, <TIMEP>, <DMIN>, <DMAX>
        # We need to preserve DINIT, TIMEP, DMIN and change DMAX
        static_pattern = r'^(\*STATIC\s*\n\s*)([0-9.eE+-]+)(,\s*)([0-9.eE+-]+)(,\s*)([0-9.eE+-]+)(,\s*)([0-9.eE+-]+)'
        
        def replace_static(match):
            dinit = match.group(2)
            timep = match.group(4)
            dmin = match.group(6)
            dmax_old = match.group(8)
            changes['dmax_old'] = float(dmax_old)
            changes['dmax_new'] = dmax_new
            changes['dmax_changed'] = True
            new_line = f"{match.group(1)}{dinit}{match.group(3)}{timep}{match.group(5)}{dmin}{match.group(7)}{dmax_new}"
            return new_line
        
        content = re.sub(static_pattern, replace_static, content, flags=re.MULTILINE)
    
    # Add TIME MARKS to OUTPUT statements if requested
    if time_marks:
        # Find OUTPUT statements and add TIME MARKS=YES if not already present
        output_pattern = r'(\*OUTPUT,\s*(?:FIELD|HISTORY)(?:,\s*[^,\n]+)*)(TIME INTERVAL=([0-9.eE+-]+))([^,\n]*(?:\n|$))'
        
        def add_time_marks(match):
            prefix = match.group(1)
            time_interval = match.group(2)
            suffix = match.group(4)
            
            if 'TIME MARKS' not in prefix:
                changes['time_marks_added'] = True
                return f"{prefix}, {time_interval}, TIME MARKS=YES{suffix}"
            return match.group(0)
        
        content_new = re.sub(output_pattern, add_time_marks, content, flags=re.MULTILINE)
        if content_new != content:
            changes['time_marks_added'] = True
            content = content_new
    
    # Add comment header if provided
    if comment:
        header_comment = f"** SENSITIVITY STUDY VARIANT\n** {comment}\n** \n"
        content = header_comment + content
    
    # Write modified content
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, 'w') as f:
        f.write(content)
    
    return changes

def main():
    """Main execution."""
    
    base_dir = Path(__file__).parent
    study_dir = base_dir / 'increment_sensitivity_study'
    study_dir.mkdir(exist_ok=True)
    
    original_deck = base_dir / 'chaboche_vp_v1_cyclic_eps005_20cycles.inp'
    exact_deck = base_dir / 'chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp'
    
    all_changes = []
    
    print("=" * 80)
    print("CHABOCHE-V1 INCREMENT-SCHEDULE SENSITIVITY STUDY PREPARATION")
    print("=" * 80)
    print()
    
    if not original_deck.exists():
        print(f"ERROR: Original deck not found: {original_deck}")
        return
    
    if not exact_deck.exists():
        print(f"WARNING: Exact-output deck not found: {exact_deck}")
        print("         Will skip exact-output variant.")
    
    # Deck 1: Original with original output (baseline)
    dest1 = study_dir / 'chaboche_eps005_20cycles_dt_original_output.inp'
    print(f"1. Creating baseline (original deck, original output settings)...")
    changes1 = copy_and_modify_deck(
        str(original_deck),
        str(dest1),
        dmax_new=None,
        time_marks=False,
        comment="Baseline: original 20-cycle deck with DMAX=0.02, original output settings"
    )
    all_changes.append(('Baseline (original)', changes1))
    print(f"   -> {dest1.name}")
    
    # Deck 2: DMAX=0.02 (same as original, but explicitly labeled)
    dest2 = study_dir / 'chaboche_eps005_20cycles_dtmax_0p02.inp'
    print(f"2. Creating DMAX=0.02 variant...")
    changes2 = copy_and_modify_deck(
        str(original_deck),
        str(dest2),
        dmax_new=0.02,
        time_marks=False,
        comment="Sensitivity study: DMAX=0.02 (same as original)"
    )
    all_changes.append(('DMAX=0.02', changes2))
    print(f"   -> {dest2.name}")
    if changes2['dmax_changed']:
        print(f"      DMAX: {changes2['dmax_old']} -> {changes2['dmax_new']}")
    
    # Deck 3: DMAX=0.01 (half)
    dest3 = study_dir / 'chaboche_eps005_20cycles_dtmax_0p01.inp'
    print(f"3. Creating DMAX=0.01 variant...")
    changes3 = copy_and_modify_deck(
        str(original_deck),
        str(dest3),
        dmax_new=0.01,
        time_marks=False,
        comment="Sensitivity study: DMAX=0.01 (half of original)"
    )
    all_changes.append(('DMAX=0.01', changes3))
    print(f"   -> {dest3.name}")
    if changes3['dmax_changed']:
        print(f"      DMAX: {changes3['dmax_old']} -> {changes3['dmax_new']}")
    
    # Deck 4: DMAX=0.005 (quarter)
    dest4 = study_dir / 'chaboche_eps005_20cycles_dtmax_0p005.inp'
    print(f"4. Creating DMAX=0.005 variant...")
    changes4 = copy_and_modify_deck(
        str(original_deck),
        str(dest4),
        dmax_new=0.005,
        time_marks=False,
        comment="Sensitivity study: DMAX=0.005 (quarter of original)"
    )
    all_changes.append(('DMAX=0.005', changes4))
    print(f"   -> {dest4.name}")
    if changes4['dmax_changed']:
        print(f"      DMAX: {changes4['dmax_old']} -> {changes4['dmax_new']}")
    
    # Deck 5: Exact-output with TIME MARKS (diagnostic)
    if exact_deck.exists():
        dest5 = study_dir / 'chaboche_eps005_20cycles_exact_timemarks_diagnostic.inp'
        print(f"5. Creating exact-output TIME MARKS diagnostic variant...")
        changes5 = copy_and_modify_deck(
            str(exact_deck),
            str(dest5),
            dmax_new=None,
            time_marks=True,
            comment="Diagnostic: exact-output deck with TIME MARKS=YES (reference for comparison)"
        )
        all_changes.append(('Exact-output (TIME MARKS)', changes5))
        print(f"   -> {dest5.name}")
        if changes5['time_marks_added']:
            print(f"      TIME MARKS=YES added to OUTPUT statements")
    
    print()
    print("=" * 80)
    print("SUMMARY OF CHANGES")
    print("=" * 80)
    for name, changes in all_changes:
        print()
        print(f"{name}:")
        if changes['dmax_changed']:
            print(f"  DMAX: {changes['dmax_old']} -> {changes['dmax_new']}")
        if changes['time_marks_added']:
            print(f"  TIME MARKS=YES added to OUTPUT")
        if not changes['dmax_changed'] and not changes['time_marks_added']:
            print(f"  (copy of original, no modifications)")
        if changes['warnings']:
            for w in changes['warnings']:
                print(f"  WARNING: {w}")
    
    print()
    print("=" * 80)
    print(f"All decks created in: {study_dir.relative_to(base_dir)}")
    print("=" * 80)

if __name__ == '__main__':
    main()
