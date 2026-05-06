from odbAccess import openOdb
odb = openOdb(path=r'D:\TUBAF\Master_Thesis\Abaqus_trial\lin_kin_1cycle.odb', readOnly=True)
step = odb.steps['Step-1']
for key in sorted(step.historyRegions.keys()):
    if 'Node' in key or 'ASSEMBLY' in key or 'PART' in key:
        print(key)
odb.close()
