from odbAccess import openOdb
odb = openOdb(path=r"D:\TUBAF\Master_Thesis\Abaqus_trial\combined_ratcheting_2cycle.odb", readOnly=True)
step = odb.steps['Step-1']
regions = step.historyRegions
print('History region count =', len(regions.keys()))
for i, k in enumerate(regions.keys()):
    if i >= 30:
        break
    outs = regions[k].historyOutputs.keys()
    print(k, '=>', list(outs)[:10])
odb.close()
