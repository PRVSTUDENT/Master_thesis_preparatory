#!/usr/bin/env python3
"""
Extract accumulated viscoplastic strain (from UMAT state variables) 

For Chaboche UMAT:
- STATEV(1) = accumulated viscoplastic strain (p)
- This maps to SDV1 in Abaqus output
"""

import csv
import os
from odbAccess import openOdb

def extract_peeq(odb_file, output_csv, sdv_index=1):
    """
    Extract accumulated viscoplastic strain from UMAT state variables
    
    Parameters
    ----------
    odb_file : str
        Path to Abaqus .odb results file
    output_csv : str
        Path to output .csv file
    sdv_index : int
        State variable index to extract (1=p, 2-7=backstress, etc.)
    """
    
    # Open the ODB
    print(f"Opening {odb_file}...")
    odb = openOdb(odb_file)
    
    peeq_data = []
    time_data = []
    
    assembly = odb.rootAssembly
    
    try:
        # Process all steps
        for step_name in sorted(odb.steps.keys()):
            step = odb.steps[step_name]
            print(f"\nProcessing step: {step_name}")
            
            for frame_idx, frame in enumerate(step.frames):
                time_val = frame.frameValue
                
                # Try to get SDV field output (State Dependent Variables)
                try:
                    sdv_field_name = f'SDV{sdv_index}'
                    sdv_field = frame.fieldOutputs[sdv_field_name]
                    
                    # Get max and average SDV in model
                    max_peeq = 0.0
                    avg_peeq = 0.0
                    sdv_values = []
                    
                    for value in sdv_field.values:
                        sdv_val = value.data
                        sdv_values.append(sdv_val)
                        if sdv_val > max_peeq:
                            max_peeq = sdv_val
                    
                    if sdv_values:
                        avg_peeq = sum(sdv_values) / len(sdv_values)
                    
                    peeq_data.append({
                        'time': time_val,
                        'max_peeq': max_peeq,
                        'avg_peeq': avg_peeq,
                        'num_elements': len(sdv_values)
                    })
                    time_data.append(time_val)
                    
                    if frame_idx % 5 == 0:
                        print(f"  Frame {frame_idx}: Time={time_val:.4f}, "
                              f"Max {sdv_field_name}={max_peeq:.8f}, "
                              f"Avg {sdv_field_name}={avg_peeq:.8f}")
                
                except KeyError:
                    print(f"  Frame {frame_idx}: {sdv_field_name} not available")
                    continue
    
    except Exception as e:
        print(f"Error processing steps: {e}")
        import traceback
        traceback.print_exc()
    
    # Write to CSV
    if peeq_data:
        print(f"\nWriting {len(peeq_data)} data points to {output_csv}...")
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time_s', 'Max_Viscoplastic_Strain', 
                           'Avg_Viscoplastic_Strain', 'Num_Elements'])
            
            for data in peeq_data:
                writer.writerow([
                    f"{data['time']:.6f}",
                    f"{data['max_peeq']:.8f}",
                    f"{data['avg_peeq']:.8f}",
                    data['num_elements']
                ])
        
        print(f"Extraction complete. Results saved to {output_csv}")
    else:
        print("No SDV data found in simulation results")
    
    odb.close()


if __name__ == "__main__":
    # Configure file paths
    odb_file = "chaboche_umat_1cycle.odb"
    output_csv = "chaboche_umat_1cycle_peeq.csv"
    
    # SDV1 corresponds to STATEV(1) = accumulated viscoplastic strain
    sdv_index = 1
    
    if os.path.exists(odb_file):
        extract_peeq(odb_file, output_csv, sdv_index)
    else:
        print(f"Error: {odb_file} not found")
        print("Run the simulation first: abaqus job=chaboche_umat_1cycle user=chaboche_umat.f")

