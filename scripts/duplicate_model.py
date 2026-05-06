# Open CAE file directly in Abaqus CAE
import sys

# Use the session and mdb directly
backupDir = mdb.models.keys()
print(f"Models before: {list(backupDir)}")

# Use the Abaqus startup module to open the file
from abaqus import *
from abaqusConstants import *

# First close any open file
try:
    session.closeFile(status=False)
except:
    pass

# Open the CAE file
cae_path = r'd:\TUBAF\Master_Thesis\Abaqus_trial\models\one_cycle\one_cycle.cae'
print(f"Opening: {cae_path}")

# Use execute to run Abaqus commands
session.newFile(modelType=STANDARD)
useOdb = session.openFile(name=cae_path, readOnly=False)
print("File opened successfully")

# Get Model-1
model1 = mdb.models['Model-1']
print(f"Found Model-1: {model1.name}")

# Duplicate it
print("Creating phase2_lin_kin...")
mdb.Model(name='phase2_lin_kin', objectToCopy=model1)
print("Model created successfully!")

# Save
print("Saving...")
mdb.saveAs(pathName=cae_path)
print("All done!")
