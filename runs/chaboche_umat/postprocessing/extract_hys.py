#!/usr/bin/env python3
"""
Extract hysteresis loop data from Chaboche UMAT Abaqus simulation

Extracts force-displacement data from .odb file using:
- U1 (displacement) from loaded nodes
- RF1 (reaction force) from loaded face reference node
"""

import csv
import os
from odbAccess import openOdb

def extract_hysteresis(odb_file, output_csv, ref_node_label='RIGHT_FACE'):
    """
    Extract force-displacement hysteresis from .odb file
    
    Uses reaction force RF1 from RIGHT_FACE nodes (loaded face).
    
    Parameters
    ----------
    odb_file : str
        Path to Abaqus .odb results file
    output_csv : str
        Path to output .csv file
    ref_node_label : str
        Reference node set label for reaction force extraction (RIGHT_FACE by default)
    """
    
    # Open the ODB
    print(f"Opening {odb_file}...")
    odb = openOdb(odb_file)
    
    displacement_data = []
    force_data = []
    time_data = []
    
    assembly = odb.rootAssembly
    
    # Get the assembly instance
    instances = assembly.instances
    if 'BLOCK_INST' not in instances:
        print("Warning: BLOCK_INST instance not found. Available instances:")
        for inst_name in instances.keys():
            print(f"  - {inst_name}")
        part_inst = list(instances.values())[0]
    else:
        part_inst = instances['BLOCK_INST']
    
    # Get RIGHT_FACE nodeset
    try:
        right_face_nodes = part_inst.nodeSets['RIGHT_FACE']
        right_face_node_labels = [node.label for node in right_face_nodes.nodes]
        print(f"Found RIGHT_FACE nodes: {right_face_node_labels}")
    except KeyError:
        print(f"Error: RIGHT_FACE node set not found in instance. Available nodesets:")
        for nset_name in part_inst.nodeSets.keys():
            print(f"  - {nset_name}")
        right_face_node_labels = []
    
    try:
        # Process all steps
        for step_name in sorted(odb.steps.keys()):
            step = odb.steps[step_name]
            print(f"\nProcessing step: {step_name}")
            
            for frame_idx, frame in enumerate(step.frames):
                time_val = frame.frameValue
                
                try:
                    # Get displacement field output (U)
                    u_field = frame.fieldOutputs['U']
                    
                    # Get reaction force field output (RF)
                    rf_field = frame.fieldOutputs['RF']
                    
                    # Get maximum displacement from RIGHT_FACE nodes
                    u_max = 0.0
                    for value in u_field.values:
                        if right_face_node_labels:
                            if value.nodeLabel in right_face_node_labels:
                                u_comp = value.data[0]  # X-displacement
                                if abs(u_comp) > abs(u_max):
                                    u_max = u_comp
                        else:
                            u_comp = value.data[0]
                            if abs(u_comp) > abs(u_max):
                                u_max = u_comp
                    
                    # Sum reaction forces in X-direction from RIGHT_FACE only
                    rf_sum = 0.0
                    count = 0
                    for value in rf_field.values:
                        if right_face_node_labels:
                            if value.nodeLabel in right_face_node_labels:
                                rf_x = value.data[0]  # RF1 (X-direction)
                                rf_sum += rf_x
                                count += 1
                        else:
                            rf_x = value.data[0]
                            rf_sum += rf_x
                            count += 1
                    
                    displacement_data.append(u_max)
                    force_data.append(rf_sum)
                    time_data.append(time_val)
                    
                    if frame_idx % 5 == 0:
                        print(f"  Frame {frame_idx}: Time={time_val:.4f}, "
                              f"U1_max={u_max:.6f}, RF1_sum={rf_sum:.2f} ({count} nodes)")
                
                except KeyError as e:
                    print(f"  Frame {frame_idx}: Field not available - {e}")
                    continue
    
    except Exception as e:
        print(f"Error processing steps: {e}")
        import traceback
        traceback.print_exc()
    
    # Write to CSV
    if displacement_data:
        print(f"\nWriting {len(displacement_data)} data points to {output_csv}...")
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time_s', 'Displacement_mm', 'ReactionForce_N'])
            
            for i in range(len(displacement_data)):
                writer.writerow([
                    f"{time_data[i]:.6f}",
                    f"{displacement_data[i]:.8f}",
                    f"{force_data[i]:.4f}"
                ])
        
        print(f"Hysteresis extraction complete. Results saved to {output_csv}")
    else:
        print("No displacement/force data found in simulation results")
    
    odb.close()


if __name__ == "__main__":
    # Configure file paths
    odb_file = "chaboche_umat_1cycle.odb"
    output_csv = "chaboche_umat_1cycle_hys.csv"
    
    if os.path.exists(odb_file):
        extract_hysteresis(odb_file, output_csv)
    else:
        print(f"Error: {odb_file} not found")
        print("Run the simulation first: abaqus job=chaboche_umat_1cycle user=chaboche_umat.f")

