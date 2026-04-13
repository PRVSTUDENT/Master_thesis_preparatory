# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2024 replay file
# Internal Version: 2023_09_21-14.55.25 RELr426 190762
# Run by pruth on Mon Apr 13 06:48:00 2026
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=222.166656494141, 
    height=132.017364501953)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
openMdb('one_cycle.cae')
#: The model database "D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\one_cycle.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='Steel_EP', 
    description='Elastic: E = 210000, nu = 0.30')
mdb.models['Model-1'].materials['Steel_EP'].Elastic(table=((210000.0, 0.3), ))
mdb.models['Model-1'].materials['Steel_EP'].Plastic(scaleStress=None, table=((
    250.0, 0.0), (300.0, 0.02), (350.0, 0.1)))
mdb.models['Model-1'].HomogeneousSolidSection(name='Sec_EP', 
    material='Steel_EP', thickness=None)
session.viewports['Viewport: 1'].view.setValues(width=12.5954, height=5.86809, 
    viewOffsetX=0.143863, viewOffsetY=-0.0462804)
p = mdb.models['Model-1'].parts['Part-1']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = p.Set(cells=cells, name='Sec_EP')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Sec_EP', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF, mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, 
    kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, 
    hourglassControl=DEFAULT, distortionControl=DEFAULT)
elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
p = mdb.models['Model-1'].parts['Part-1']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON, mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
    predefinedFields=ON, connectors=ON, optimizationTasks=OFF, 
    geometricRestrictions=OFF, stopConditions=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON, loads=OFF, 
    bcs=OFF, predefinedFields=OFF, connectors=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-2', part=p, dependent=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
    predefinedFields=ON, connectors=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF, 
    predefinedFields=OFF, connectors=OFF, adaptiveMeshConstraints=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
    predefinedFields=ON, connectors=ON, adaptiveMeshConstraints=OFF)
mdb.models['Model-1'].boundaryConditions['BC-right'].setValues(u1=0.5)
mdb.models['Model-1'].boundaryConditions['BC-right'].setValues(amplitude=UNSET)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF, 
    predefinedFields=OFF, connectors=OFF)
mdb.Job(name='mono_ep_test', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['mono_ep_test'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "mono_ep_test.inp".
mdb.jobs['mono_ep_test'].submit(consistencyChecking=OFF)
#: The job input file "mono_ep_test.inp" has been submitted for analysis.
#: Job mono_ep_test: Analysis Input File Processor completed successfully.
#: Job mono_ep_test: Abaqus/Standard completed successfully.
#: Job mono_ep_test completed successfully. 
session.viewports['Viewport: 1'].setValues(displayedObject=None)
o1 = session.openOdb(
    name='D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
#: Model: D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     2
#: Number of Meshes:             2
#: Number of Element Sets:       7
#: Number of Node Sets:          7
#: Number of Steps:              1
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    DEFORMED, ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.9694, 
    farPlane=28.1191, width=13.1935, height=6.14672, viewOffsetX=0.260249, 
    viewOffsetY=0.192006)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='PEEQ', outputPosition=INTEGRATION_POINT, )
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    DEFORMED, ))
session.viewports['Viewport: 1'].animationController.setValues(
    animationType=SCALE_FACTOR)
session.viewports['Viewport: 1'].animationController.play(duration=UNLIMITED)
session.viewports['Viewport: 1'].animationController.setValues(
    animationType=TIME_HISTORY)
session.viewports['Viewport: 1'].animationController.play(duration=UNLIMITED)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    ORIENT_ON_DEF, ))
#: Warning: Material orientation information is not available in the current frame for any elements in the current display group. Please make sure that the primary variable is element-based and orientations were defined in the pertinent solid/shell sections.
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=ON)
mdb.models['Model-1'].HistoryOutputRequest(name='H-RF-left', 
    createStepName='Step-1', variables=('IRF1', 'IRF2', 'IRF3', 'IRM1', 'IRM2', 
    'IRM3'))
regionDef=mdb.models['Model-1'].rootAssembly.allInstances['Part-1-1'].sets['Sec_EP']
mdb.models['Model-1'].HistoryOutputRequest(name='H-U-right', 
    createStepName='Step-1', variables=('IRA1', 'IRA2', 'IRA3', 'IRAR1', 
    'IRAR2', 'IRAR3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
regionDef=mdb.models['Model-1'].rootAssembly.allInstances['Part-1-1'].sets['Sec_EP']
mdb.models['Model-1'].historyOutputRequests['H-RF-left'].setValues(variables=(
    'IRF1', 'IRF2', 'IRF3', 'IRM1', 'IRM2', 'IRM3'), region=regionDef, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.2243, 
    farPlane=28.256, width=12.9675, height=6.27751, cameraTarget=(2.41523, 
    1.20935, 5.50561), viewOffsetX=5.42472, viewOffsetY=0.497884)
session.viewports['Viewport: 1'].view.setValues(nearPlane=20.6898, 
    farPlane=30.5617, width=16.5367, height=8.0053, cameraPosition=(-8.26277, 
    8.7964, 21.603), cameraUpVector=(-0.117189, 0.628578, -0.768867), 
    cameraTarget=(2.49473, 0.377113, 4.00958), viewOffsetX=6.91779, 
    viewOffsetY=0.634919)
session.viewports['Viewport: 1'].view.setValues(nearPlane=18.288, 
    farPlane=31.7006, width=14.6171, height=7.07601, cameraPosition=(-15.9516, 
    -4.59378, 13.5069), cameraUpVector=(-0.0829708, 0.930843, -0.355875), 
    cameraTarget=(3.19142, 0.762884, 3.45773), viewOffsetX=6.11475, 
    viewOffsetY=0.561215)
session.viewports['Viewport: 1'].view.setValues(nearPlane=18.7876, 
    farPlane=31.201, width=11.0657, height=5.35683, viewOffsetX=1.28827, 
    viewOffsetY=1.60975)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.6832, 
    farPlane=29.3508, width=9.8262, height=4.7568, cameraPosition=(-17.9267, 
    -2.40013, 0.889907), cameraUpVector=(0.136751, 0.984122, 0.11315), 
    cameraTarget=(3.86589, 1.35094, 3.5631), viewOffsetX=1.14397, 
    viewOffsetY=1.42944)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.6674, 
    farPlane=29.1076, width=9.8169, height=4.7523, cameraPosition=(-17.6533, 
    -3.18286, 0.193335), cameraUpVector=(0.104863, 0.991547, 0.0764128), 
    cameraTarget=(3.90118, 1.31174, 3.56017), viewOffsetX=1.14289, 
    viewOffsetY=1.42809)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.405, 
    farPlane=29.3699, width=13.1657, height=6.37345, viewOffsetX=1.55052, 
    viewOffsetY=1.42087)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.9159, 
    farPlane=29.8351, width=13.5757, height=6.57192, cameraPosition=(-18.3968, 
    -0.4948, 2.88529), cameraUpVector=(0.231568, 0.967103, 0.105297), 
    cameraTarget=(3.79263, 1.33265, 3.53539), viewOffsetX=1.59881, 
    viewOffsetY=1.46512)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=19.8885, 
    farPlane=31.4395, width=15.9613, height=7.72678, cameraPosition=(-13.1146, 
    -1.34831, 19.0353), cameraUpVector=(0.0628954, 0.96934, -0.237539), 
    cameraTarget=(2.78958, 1.03802, 3.62438), viewOffsetX=1.87976, 
    viewOffsetY=1.72258)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['Part-1-2'].faces
faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
a.Set(faces=faces1, name='Set_Left_Nodes')
#: The set 'Set_Left_Nodes' has been created (1 face).
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
del mdb.models['Model-1'].rootAssembly.sets['Set_Left_Nodes']
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-1'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#0:14 #3d00000 #9c07bd80 #73 ]', ), )
n2 = a.instances['Part-1-2'].nodes
nodes2 = n2.getSequenceFromMask(mask=('[#0:14 #3d20000 #fff7bd80 #1fff ]', ), )
a.Set(nodes=nodes1+nodes2, name='Set_Left_Nodes')
#: The set 'Set_Left_Nodes' has been created (65 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.9604, 
    farPlane=29.2978, width=13.6114, height=6.58919, cameraPosition=(19.8439, 
    0.743104, 19.4798), cameraUpVector=(-0.440325, 0.896462, 0.0497005), 
    cameraTarget=(2.43396, 0.741562, 5.58636), viewOffsetX=1.60301, 
    viewOffsetY=1.46897)
session.viewports['Viewport: 1'].view.setValues(nearPlane=17.6464, 
    farPlane=28.6118, width=8.63271, height=4.17904, viewOffsetX=6.92473, 
    viewOffsetY=-1.43819)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-2'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#1ffffff ]', ), )
a.Set(nodes=nodes1, name='Set_Right_Nodes')
#: The set 'Set_Right_Nodes' has been created (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.6699, 
    farPlane=29.5883, width=19.6315, height=9.50347, viewOffsetX=9.09654, 
    viewOffsetY=-0.407022)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.5719, 
    farPlane=29.6863, width=19.516, height=9.4476, cameraPosition=(19.84, 
    0.943572, 19.4847), cameraUpVector=(-0.352473, 0.933871, -0.0603908), 
    cameraTarget=(2.43003, 0.94203, 5.59127), viewOffsetX=9.04305, 
    viewOffsetY=-0.404629)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.5703, 
    farPlane=29.688, width=19.5141, height=9.44667, cameraPosition=(19.8441, 
    1.02727, 19.4796), cameraUpVector=(-0.314855, 0.943029, -0.107531), 
    cameraTarget=(2.43408, 1.02573, 5.58618), viewOffsetX=9.04216, 
    viewOffsetY=-0.404589)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.5705, 
    farPlane=29.6878, width=19.5143, height=9.44676, cameraPosition=(19.8499, 
    1.09484, 19.4724), cameraUpVector=(-0.284078, 0.947605, -0.146098), 
    cameraTarget=(2.43983, 1.0933, 5.57896), viewOffsetX=9.04224, 
    viewOffsetY=-0.404593)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.5705, 
    farPlane=29.6879, width=19.5143, height=9.44676, cameraPosition=(19.8829, 
    1.30627, 19.431), cameraUpVector=(-0.185311, 0.944899, -0.269864), 
    cameraTarget=(2.47284, 1.30473, 5.53757), viewOffsetX=9.04224, 
    viewOffsetY=-0.404593)
session.viewports['Viewport: 1'].view.setValues(nearPlane=11.8543, 
    farPlane=25.8077, width=13.9602, height=6.75806, cameraPosition=(22.989, 
    4.72314, -4.6756), cameraUpVector=(-0.360161, 0.879036, 0.312376), 
    cameraTarget=(3.82988, 0.993644, 6.05553), viewOffsetX=6.46868, 
    viewOffsetY=-0.289439)
session.viewports['Viewport: 1'].view.setValues(nearPlane=15.4545, 
    farPlane=21.7598, width=18.1999, height=8.8105, cameraPosition=(3.08056, 
    9.9164, -15.299), cameraUpVector=(0.147749, 0.738157, 0.658251), 
    cameraTarget=(4.80572, 0.915452, 5.00238), viewOffsetX=8.43323, 
    viewOffsetY=-0.377342)
session.viewports['Viewport: 1'].view.setValues(nearPlane=15.1451, 
    farPlane=21.3627, width=17.8355, height=8.63411, cameraPosition=(4.42972, 
    4.01258, -16.9986), cameraUpVector=(0.355171, 0.826157, 0.4374), 
    cameraTarget=(4.78213, 0.646866, 5.01699), viewOffsetX=8.26439, 
    viewOffsetY=-0.369787)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.1862, 
    farPlane=26.204, width=16.7064, height=8.08746, cameraPosition=(-9.25705, 
    7.87386, -11.7602), cameraUpVector=(0.623966, 0.745717, 0.233608), 
    cameraTarget=(4.62319, 0.646621, 4.09047), viewOffsetX=7.74115, 
    viewOffsetY=-0.346375)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.2992, 
    farPlane=26.091, width=15.8938, height=7.6941, viewOffsetX=2.10634, 
    viewOffsetY=-0.158766)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-2'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#0:15 #fff00000 #1fff ]', ), )
a.Set(nodes=nodes1, name='Set_Left_Nodes')
#: The set 'Set_Left_Nodes' has been edited (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.8556, 
    farPlane=22.3906, width=16.5123, height=7.9935, cameraPosition=(0.713238, 
    5.81134, -16.5039), cameraUpVector=(0.404274, 0.800212, 0.44297), 
    cameraTarget=(4.81143, 0.67483, 4.77893), viewOffsetX=2.1883, 
    viewOffsetY=-0.164944)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.8021, 
    farPlane=22.4441, width=16.4529, height=7.96473, cameraPosition=(0.728095, 
    6.00233, -16.4607), cameraUpVector=(0.270499, 0.836029, 0.477374), 
    cameraTarget=(4.82629, 0.865824, 4.82216), viewOffsetX=2.18042, 
    viewOffsetY=-0.16435)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-2'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#1ffffff ]', ), )
a.Set(nodes=nodes1, name='Set_Right_Nodes')
#: The set 'Set_Right_Nodes' has been edited (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
a = mdb.models['Model-1'].rootAssembly
del a.features['Part-1-2']
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=ON)
regionDef=mdb.models['Model-1'].rootAssembly.sets['Set_Left_Nodes']
mdb.models['Model-1'].historyOutputRequests['H-RF-left'].setValues(
    region=regionDef)
regionDef=mdb.models['Model-1'].rootAssembly.sets['Set_Right_Nodes']
mdb.models['Model-1'].historyOutputRequests['H-U-right'].setValues(
    region=regionDef)
mdb.models['Model-1'].historyOutputRequests['H-U-right'].setValues(variables=(
    'U1', 'U2', 'U3', 'UR1', 'UR2', 'UR3', 'IRA1', 'IRA2', 'IRA3', 'IRAR1', 
    'IRAR2', 'IRAR3'))
mdb.models['Model-1'].historyOutputRequests['H-RF-left'].setValues(variables=(
    'RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3', 'IRF1', 'IRF2', 'IRF3', 'IRM1', 
    'IRM2', 'IRM3'))
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=ON)
del mdb.models['Model-1'].historyOutputRequests['H-RF-left']
del mdb.models['Model-1'].historyOutputRequests['H-U-right']
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=OFF)
del mdb.models['Model-1'].rootAssembly.sets['Set_Left_Nodes']
del mdb.models['Model-1'].rootAssembly.sets['Set_Right_Nodes']
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.6904, 
    farPlane=22.5559, width=17.448, height=7.90464, cameraPosition=(0.717099, 
    6.17009, -16.4181), cameraUpVector=(0.148292, 0.850624, 0.504428), 
    cameraTarget=(4.81529, 1.03358, 4.86476), viewOffsetX=2.16397, 
    viewOffsetY=-0.16311)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.705, 
    farPlane=22.5413, width=17.4653, height=7.91248, cameraPosition=(0.674562, 
    6.36529, -16.3628), cameraUpVector=(0.00026915, 0.846747, 0.531996), 
    cameraTarget=(4.77275, 1.22878, 4.92006), viewOffsetX=2.16612, 
    viewOffsetY=-0.163272)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.8268, 
    farPlane=28.3449, width=17.61, height=7.97804, cameraPosition=(-15.5829, 
    0.592774, -6.21797), cameraUpVector=(0.0255334, 0.84501, 0.53414), 
    cameraTarget=(4.16194, 1.77599, 4.02315), viewOffsetX=2.18407, 
    viewOffsetY=-0.164625)
session.viewports['Viewport: 1'].view.setValues(nearPlane=19.8438, 
    farPlane=31.6734, width=23.5687, height=10.6776, cameraPosition=(-11.4553, 
    4.33737, 20.5453), cameraUpVector=(0.159972, 0.874457, -0.457966), 
    cameraTarget=(2.68584, 0.895091, 3.68351), viewOffsetX=2.9231, 
    viewOffsetY=-0.220329)
session.viewports['Viewport: 1'].view.setValues(nearPlane=14.4948, 
    farPlane=29.4322, width=17.2156, height=7.79937, cameraPosition=(21.7803, 
    9.195, 13.7306), cameraUpVector=(-0.58716, 0.769554, -0.251056), 
    cameraTarget=(2.63038, 1.05406, 5.78405), viewOffsetX=2.13516, 
    viewOffsetY=-0.160938)
session.viewports['Viewport: 1'].view.setValues(nearPlane=13.8784, 
    farPlane=27.9219, width=16.4836, height=7.46771, cameraPosition=(26.4077, 
    1.87022, 2.75082), cameraUpVector=(-0.335145, 0.891357, 0.305221), 
    cameraTarget=(4.44938, 0.279776, 6.13409), viewOffsetX=2.04436, 
    viewOffsetY=-0.154094)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-1'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#1ffffff ]', ), )
a.Set(nodes=nodes1, name='Set_Left_Nodes')
#: The set 'Set_Left_Nodes' has been created (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.9915, 
    farPlane=27.7131, width=20.1811, height=9.14281, cameraPosition=(-7.97557, 
    5.58534, 18.7078), cameraUpVector=(0.518885, 0.829372, -0.207122), 
    cameraTarget=(3.7594, 2.0096, 0.116203), viewOffsetX=2.50293, 
    viewOffsetY=-0.188659)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-1'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#1ffffff ]', ), )
a.Set(nodes=nodes1, name='Set_Left_Nodes')
#: The set 'Set_Left_Nodes' has been edited (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
a = mdb.models['Model-1'].rootAssembly
n1 = a.instances['Part-1-1'].nodes
nodes1 = n1.getSequenceFromMask(mask=('[#0:15 #fff00000 #1fff ]', ), )
a.Set(nodes=nodes1, name='Set_Right_Nodes')
#: The set 'Set_Right_Nodes' has been created (25 nodes).
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=ON)
regionDef=mdb.models['Model-1'].rootAssembly.sets['Set_Left_Nodes']
mdb.models['Model-1'].HistoryOutputRequest(name='H-RF-left', 
    createStepName='Step-1', variables=('RF1', 'RF2', 'RF3', 'RM1', 'RM2', 
    'RM3', 'RT', 'RM', 'RWM', 'CF1', 'CF2', 'CF3', 'CM1', 'CM2', 'CM3', 'CW', 
    'SF1', 'SF2', 'SF3', 'SM1', 'SM2', 'SM3', 'BIMOM', 'SQEQ', 'TF1', 'TF2', 
    'TF3', 'TM1', 'TM2', 'TM3', 'VF1', 'VF2', 'VF3', 'VM1', 'VM2', 'VM3', 
    'RFMAG', 'ESF1', 'NFORC', 'NFORCSO', 'RBFOR', 'IRF1', 'IRF2', 'IRF3', 
    'IRM1', 'IRM2', 'IRM3'), region=regionDef, sectionPoints=DEFAULT, 
    rebar=EXCLUDE)
regionDef=mdb.models['Model-1'].rootAssembly.sets['Set_Right_Nodes']
mdb.models['Model-1'].HistoryOutputRequest(name='H-U-right', 
    createStepName='Step-1', variables=('U1', 'U2', 'U3', 'UR1', 'UR2', 'UR3', 
    'UT', 'UR', 'V1', 'V2', 'V3', 'VR1', 'VR2', 'VR3', 'VT', 'VR', 'WARP', 
    'RBANG', 'RBROT', 'UMAG', 'IRA1', 'IRA2', 'IRA3', 'IRAR1', 'IRAR2', 
    'IRAR3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=OFF)
mdb.jobs['mono_ep_test'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "mono_ep_test.inp".
mdb.jobs['mono_ep_test'].submit(consistencyChecking=OFF)
#: The job input file "mono_ep_test.inp" has been submitted for analysis.
#: Job mono_ep_test: Analysis Input File Processor completed successfully.
#: Job mono_ep_test: Abaqus/Standard completed successfully.
#: Job mono_ep_test completed successfully. 
session.viewports['Viewport: 1'].setValues(displayedObject=None)
o1 = session.openOdb(
    name='D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
#: Model: D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       5
#: Number of Node Sets:          7
#: Number of Steps:              1
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    DEFORMED, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    UNDEFORMED, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    DEFORMED, ))
session.viewports['Viewport: 1'].view.setValues(width=11.0735, height=5.01671, 
    viewOffsetX=-0.122118, viewOffsetY=0.035723)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.1214, 
    farPlane=28.9065, width=10.0636, height=4.55922, cameraPosition=(23.9519, 
    11.9881, 7.75842), cameraUpVector=(-0.781803, 0.62351, -0.00432706), 
    cameraTarget=(5.29829, 0.757777, 0.88345), viewOffsetX=-0.110982, 
    viewOffsetY=0.0324653)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.8808, 
    farPlane=27.9107, width=10.5377, height=4.77399, cameraPosition=(19.086, 
    14.2329, -10.9118), cameraUpVector=(0.0567449, 0.249553, 0.966697), 
    cameraTarget=(5.18115, 0.807176, 1.24342), viewOffsetX=-0.11621, 
    viewOffsetY=0.0339947)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.8316, 
    farPlane=27.96, width=10.507, height=4.76009, cameraPosition=(19.1004, 
    14.1669, -10.9683), cameraUpVector=(-0.351863, 0.508843, 0.785666), 
    cameraTarget=(5.19553, 0.741173, 1.18697), viewOffsetX=-0.115872, 
    viewOffsetY=0.0338957)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.8349, 
    farPlane=27.9569, width=10.509, height=4.76101, cameraPosition=(19.1032, 
    14.161, -10.9716), cameraUpVector=(-0.385016, 0.521347, 0.761551), 
    cameraTarget=(5.19835, 0.735287, 1.18369), viewOffsetX=-0.115895, 
    viewOffsetY=0.0339023)
session.viewports['Viewport: 1'].view.setValues(nearPlane=16.2061, 
    farPlane=28.3838, width=10.1165, height=4.58318, cameraPosition=(-11.3034, 
    7.11106, -12.3188), cameraUpVector=(0.388462, 0.808922, 0.441297), 
    cameraTarget=(5.7955, 0.804693, 1.4363), viewOffsetX=-0.111566, 
    viewOffsetY=0.032636)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    UNDEFORMED, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    DEFORMED, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    UNDEFORMED, ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))
odb = session.odbs['D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb']
xy1 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 1 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c1 = session.Curve(xyData=xy1)
xy2 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 2 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c2 = session.Curve(xyData=xy2)
xy3 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 3 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c3 = session.Curve(xyData=xy3)
xy4 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 4 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c4 = session.Curve(xyData=xy4)
xy5 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 5 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c5 = session.Curve(xyData=xy5)
xy6 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 6 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c6 = session.Curve(xyData=xy6)
xy7 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 7 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c7 = session.Curve(xyData=xy7)
xy8 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 8 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c8 = session.Curve(xyData=xy8)
xy9 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 9 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c9 = session.Curve(xyData=xy9)
xy10 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 10 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c10 = session.Curve(xyData=xy10)
xy11 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 11 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c11 = session.Curve(xyData=xy11)
xy12 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 12 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c12 = session.Curve(xyData=xy12)
xy13 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 13 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c13 = session.Curve(xyData=xy13)
xy14 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 14 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c14 = session.Curve(xyData=xy14)
xy15 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 15 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c15 = session.Curve(xyData=xy15)
xy16 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 16 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c16 = session.Curve(xyData=xy16)
xy17 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 17 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c17 = session.Curve(xyData=xy17)
xy18 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 18 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c18 = session.Curve(xyData=xy18)
xy19 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 19 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c19 = session.Curve(xyData=xy19)
xy20 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 20 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c20 = session.Curve(xyData=xy20)
xy21 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 21 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c21 = session.Curve(xyData=xy21)
xy22 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 22 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c22 = session.Curve(xyData=xy22)
xy23 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 23 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c23 = session.Curve(xyData=xy23)
xy24 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 24 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c24 = session.Curve(xyData=xy24)
xy25 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 25 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c25 = session.Curve(xyData=xy25)
xy26 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 1 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c26 = session.Curve(xyData=xy26)
xy27 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 2 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c27 = session.Curve(xyData=xy27)
xy28 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 3 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c28 = session.Curve(xyData=xy28)
xy29 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 4 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c29 = session.Curve(xyData=xy29)
xy30 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 5 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c30 = session.Curve(xyData=xy30)
xy31 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 6 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c31 = session.Curve(xyData=xy31)
xy32 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 7 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c32 = session.Curve(xyData=xy32)
xy33 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 8 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c33 = session.Curve(xyData=xy33)
xy34 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 9 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c34 = session.Curve(xyData=xy34)
xy35 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 10 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c35 = session.Curve(xyData=xy35)
xy36 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 11 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c36 = session.Curve(xyData=xy36)
xy37 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 12 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c37 = session.Curve(xyData=xy37)
xy38 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 13 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c38 = session.Curve(xyData=xy38)
xy39 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 14 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c39 = session.Curve(xyData=xy39)
xy40 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 15 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c40 = session.Curve(xyData=xy40)
xy41 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 16 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c41 = session.Curve(xyData=xy41)
xy42 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 17 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c42 = session.Curve(xyData=xy42)
xy43 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 18 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c43 = session.Curve(xyData=xy43)
xy44 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 19 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c44 = session.Curve(xyData=xy44)
xy45 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 20 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c45 = session.Curve(xyData=xy45)
xy46 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 21 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c46 = session.Curve(xyData=xy46)
xy47 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 22 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c47 = session.Curve(xyData=xy47)
xy48 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 23 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c48 = session.Curve(xyData=xy48)
xy49 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 24 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c49 = session.Curve(xyData=xy49)
xy50 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 25 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c50 = session.Curve(xyData=xy50)
xyp = session.XYPlot('XYPlot-1')
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
chart.setValues(curvesToPlot=(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, 
    c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24, c25, c26, 
    c27, c28, c29, c30, c31, c32, c33, c34, c35, c36, c37, c38, c39, c40, c41, 
    c42, c43, c44, c45, c46, c47, c48, c49, c50, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
odb = session.odbs['D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb']
xy0 = session.XYDataFromHistory(name='RFMAG N: 1 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 1 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c0 = session.Curve(xyData=xy0)
xy1 = session.XYDataFromHistory(name='RFMAG N: 2 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 2 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c1 = session.Curve(xyData=xy1)
xy2 = session.XYDataFromHistory(name='RFMAG N: 3 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 3 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c2 = session.Curve(xyData=xy2)
xy3 = session.XYDataFromHistory(name='RFMAG N: 4 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 4 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c3 = session.Curve(xyData=xy3)
xy4 = session.XYDataFromHistory(name='RFMAG N: 5 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 5 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c4 = session.Curve(xyData=xy4)
xy5 = session.XYDataFromHistory(name='RFMAG N: 6 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 6 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c5 = session.Curve(xyData=xy5)
xy6 = session.XYDataFromHistory(name='RFMAG N: 7 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 7 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c6 = session.Curve(xyData=xy6)
xy7 = session.XYDataFromHistory(name='RFMAG N: 8 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 8 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c7 = session.Curve(xyData=xy7)
xy8 = session.XYDataFromHistory(name='RFMAG N: 9 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 9 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c8 = session.Curve(xyData=xy8)
xy9 = session.XYDataFromHistory(name='RFMAG N: 10 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 10 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c9 = session.Curve(xyData=xy9)
xy10 = session.XYDataFromHistory(name='RFMAG N: 11 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 11 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c10 = session.Curve(xyData=xy10)
xy11 = session.XYDataFromHistory(name='RFMAG N: 12 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 12 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c11 = session.Curve(xyData=xy11)
xy12 = session.XYDataFromHistory(name='RFMAG N: 13 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 13 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c12 = session.Curve(xyData=xy12)
xy13 = session.XYDataFromHistory(name='RFMAG N: 14 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 14 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c13 = session.Curve(xyData=xy13)
xy14 = session.XYDataFromHistory(name='RFMAG N: 15 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 15 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c14 = session.Curve(xyData=xy14)
xy15 = session.XYDataFromHistory(name='RFMAG N: 16 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 16 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c15 = session.Curve(xyData=xy15)
xy16 = session.XYDataFromHistory(name='RFMAG N: 17 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 17 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c16 = session.Curve(xyData=xy16)
xy17 = session.XYDataFromHistory(name='RFMAG N: 18 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 18 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c17 = session.Curve(xyData=xy17)
xy18 = session.XYDataFromHistory(name='RFMAG N: 19 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 19 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c18 = session.Curve(xyData=xy18)
xy19 = session.XYDataFromHistory(name='RFMAG N: 20 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 20 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c19 = session.Curve(xyData=xy19)
xy20 = session.XYDataFromHistory(name='RFMAG N: 21 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 21 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c20 = session.Curve(xyData=xy20)
xy21 = session.XYDataFromHistory(name='RFMAG N: 22 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 22 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c21 = session.Curve(xyData=xy21)
xy22 = session.XYDataFromHistory(name='RFMAG N: 23 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 23 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c22 = session.Curve(xyData=xy22)
xy23 = session.XYDataFromHistory(name='RFMAG N: 24 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 24 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c23 = session.Curve(xyData=xy23)
xy24 = session.XYDataFromHistory(name='RFMAG N: 25 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction Force Magnitude: RFMAG at Node 25 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c24 = session.Curve(xyData=xy24)
xy25 = session.XYDataFromHistory(name='RF1 N: 1 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 1 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c25 = session.Curve(xyData=xy25)
xy26 = session.XYDataFromHistory(name='RF1 N: 2 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 2 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c26 = session.Curve(xyData=xy26)
xy27 = session.XYDataFromHistory(name='RF1 N: 3 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 3 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c27 = session.Curve(xyData=xy27)
xy28 = session.XYDataFromHistory(name='RF1 N: 4 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 4 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c28 = session.Curve(xyData=xy28)
xy29 = session.XYDataFromHistory(name='RF1 N: 5 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 5 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c29 = session.Curve(xyData=xy29)
xy30 = session.XYDataFromHistory(name='RF1 N: 6 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 6 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c30 = session.Curve(xyData=xy30)
xy31 = session.XYDataFromHistory(name='RF1 N: 7 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 7 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c31 = session.Curve(xyData=xy31)
xy32 = session.XYDataFromHistory(name='RF1 N: 8 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 8 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c32 = session.Curve(xyData=xy32)
xy33 = session.XYDataFromHistory(name='RF1 N: 9 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 9 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c33 = session.Curve(xyData=xy33)
xy34 = session.XYDataFromHistory(name='RF1 N: 10 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 10 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c34 = session.Curve(xyData=xy34)
xy35 = session.XYDataFromHistory(name='RF1 N: 11 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 11 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c35 = session.Curve(xyData=xy35)
xy36 = session.XYDataFromHistory(name='RF1 N: 12 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 12 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c36 = session.Curve(xyData=xy36)
xy37 = session.XYDataFromHistory(name='RF1 N: 13 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 13 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c37 = session.Curve(xyData=xy37)
xy38 = session.XYDataFromHistory(name='RF1 N: 14 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 14 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c38 = session.Curve(xyData=xy38)
xy39 = session.XYDataFromHistory(name='RF1 N: 15 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 15 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c39 = session.Curve(xyData=xy39)
xy40 = session.XYDataFromHistory(name='RF1 N: 16 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 16 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c40 = session.Curve(xyData=xy40)
xy41 = session.XYDataFromHistory(name='RF1 N: 17 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 17 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c41 = session.Curve(xyData=xy41)
xy42 = session.XYDataFromHistory(name='RF1 N: 18 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 18 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c42 = session.Curve(xyData=xy42)
xy43 = session.XYDataFromHistory(name='RF1 N: 19 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 19 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c43 = session.Curve(xyData=xy43)
xy44 = session.XYDataFromHistory(name='RF1 N: 20 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 20 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c44 = session.Curve(xyData=xy44)
xy45 = session.XYDataFromHistory(name='RF1 N: 21 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 21 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c45 = session.Curve(xyData=xy45)
xy46 = session.XYDataFromHistory(name='RF1 N: 22 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 22 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c46 = session.Curve(xyData=xy46)
xy47 = session.XYDataFromHistory(name='RF1 N: 23 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 23 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c47 = session.Curve(xyData=xy47)
xy48 = session.XYDataFromHistory(name='RF1 N: 24 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 24 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c48 = session.Curve(xyData=xy48)
xy49 = session.XYDataFromHistory(name='RF1 N: 25 NSET SET_LEFT_NODES-1', 
    odb=odb, 
    outputVariableName='Reaction force: RF1 at Node 25 in NSET SET_LEFT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
c49 = session.Curve(xyData=xy49)
xyp = session.xyPlots['XYPlot-1']
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
chart.setValues(curvesToPlot=(c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, 
    c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24, c25, c26, 
    c27, c28, c29, c30, c31, c32, c33, c34, c35, c36, c37, c38, c39, c40, c41, 
    c42, c43, c44, c45, c46, c47, c48, c49, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
odb = session.odbs['D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb']
xy1 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 501 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c1 = session.Curve(xyData=xy1)
xy2 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 502 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c2 = session.Curve(xyData=xy2)
xy3 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 503 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c3 = session.Curve(xyData=xy3)
xy4 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 504 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c4 = session.Curve(xyData=xy4)
xy5 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 505 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c5 = session.Curve(xyData=xy5)
xy6 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 506 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c6 = session.Curve(xyData=xy6)
xy7 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 507 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c7 = session.Curve(xyData=xy7)
xy8 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 508 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c8 = session.Curve(xyData=xy8)
xy9 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 509 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c9 = session.Curve(xyData=xy9)
xy10 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 510 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c10 = session.Curve(xyData=xy10)
xy11 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 511 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c11 = session.Curve(xyData=xy11)
xy12 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 512 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c12 = session.Curve(xyData=xy12)
xy13 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 513 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c13 = session.Curve(xyData=xy13)
xy14 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 514 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c14 = session.Curve(xyData=xy14)
xy15 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 515 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c15 = session.Curve(xyData=xy15)
xy16 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 516 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c16 = session.Curve(xyData=xy16)
xy17 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 517 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c17 = session.Curve(xyData=xy17)
xy18 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 518 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c18 = session.Curve(xyData=xy18)
xy19 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 519 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c19 = session.Curve(xyData=xy19)
xy20 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 520 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c20 = session.Curve(xyData=xy20)
xy21 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 521 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c21 = session.Curve(xyData=xy21)
xy22 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 522 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c22 = session.Curve(xyData=xy22)
xy23 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 523 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c23 = session.Curve(xyData=xy23)
xy24 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 524 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c24 = session.Curve(xyData=xy24)
xy25 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 525 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c25 = session.Curve(xyData=xy25)
xyp = session.xyPlots['XYPlot-1']
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
chart.setValues(curvesToPlot=(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, 
    c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24, c25, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
odb = session.odbs['D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test.odb']
session.XYDataFromHistory(name='U1 N: 501 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 501 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 502 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 502 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 503 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 503 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 504 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 504 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 505 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 505 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 506 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 506 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 507 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 507 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 508 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 508 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 509 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 509 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 510 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 510 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 511 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 511 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 512 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 512 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 513 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 513 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 514 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 514 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 515 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 515 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 516 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 516 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 517 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 517 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 518 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 518 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 519 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 519 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 520 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 520 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 521 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 521 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 522 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 522 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 523 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 523 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 524 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 524 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
session.XYDataFromHistory(name='U1 N: 525 NSET SET_RIGHT_NODES-1', odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 525 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), __linkedVpName__='Viewport: 1')
xy1 = session.xyDataObjects['RF1 N: 1 NSET SET_LEFT_NODES-1']
xy2 = session.xyDataObjects['RF1 N: 2 NSET SET_LEFT_NODES-1']
xy3 = session.xyDataObjects['RF1 N: 3 NSET SET_LEFT_NODES-1']
xy4 = session.xyDataObjects['RF1 N: 4 NSET SET_LEFT_NODES-1']
xy5 = session.xyDataObjects['RF1 N: 5 NSET SET_LEFT_NODES-1']
xy6 = session.xyDataObjects['RF1 N: 6 NSET SET_LEFT_NODES-1']
xy7 = session.xyDataObjects['RF1 N: 7 NSET SET_LEFT_NODES-1']
xy8 = session.xyDataObjects['RF1 N: 8 NSET SET_LEFT_NODES-1']
xy9 = session.xyDataObjects['RF1 N: 9 NSET SET_LEFT_NODES-1']
xy10 = session.xyDataObjects['RF1 N: 10 NSET SET_LEFT_NODES-1']
xy11 = session.xyDataObjects['RF1 N: 11 NSET SET_LEFT_NODES-1']
xy12 = session.xyDataObjects['RF1 N: 12 NSET SET_LEFT_NODES-1']
xy13 = session.xyDataObjects['RF1 N: 13 NSET SET_LEFT_NODES-1']
xy14 = session.xyDataObjects['RF1 N: 14 NSET SET_LEFT_NODES-1']
xy15 = session.xyDataObjects['RF1 N: 15 NSET SET_LEFT_NODES-1']
xy16 = session.xyDataObjects['RF1 N: 16 NSET SET_LEFT_NODES-1']
xy17 = session.xyDataObjects['RF1 N: 17 NSET SET_LEFT_NODES-1']
xy18 = session.xyDataObjects['RF1 N: 18 NSET SET_LEFT_NODES-1']
xy19 = session.xyDataObjects['RF1 N: 19 NSET SET_LEFT_NODES-1']
xy20 = session.xyDataObjects['RF1 N: 20 NSET SET_LEFT_NODES-1']
xy21 = session.xyDataObjects['RF1 N: 21 NSET SET_LEFT_NODES-1']
xy22 = session.xyDataObjects['RF1 N: 22 NSET SET_LEFT_NODES-1']
xy23 = session.xyDataObjects['RF1 N: 23 NSET SET_LEFT_NODES-1']
xy24 = session.xyDataObjects['RF1 N: 24 NSET SET_LEFT_NODES-1']
xy25 = session.xyDataObjects['RF1 N: 25 NSET SET_LEFT_NODES-1']
xy26 = sum((xy1, xy2, xy3, xy4, xy5, xy6, xy7, xy8, xy9, xy10, xy11, xy12, 
    xy13, xy14, xy15, xy16, xy17, xy18, xy19, xy20, xy21, xy22, xy23, xy24, 
    xy25))
xy26.setValues(
    sourceDescription='sum ( ( "RF1 N: 1 NSET SET_LEFT_NODES-1", "RF1 N: 2 NSET SET_LEFT_NODES-1", "RF1 N: 3 NSET SET_LEFT_NODES-1", "RF1 N: 4 NSET SET_LEFT_NODES-1", "RF1 N: 5 NSET SET_LEFT_NODES-1", "RF1 N: 6 NSET SET_LEFT_NODES-1", "RF1 N: 7 NSET SET_LEFT_NODES-1", "RF1 N: 8 NSET SET_LEFT_NODES-1", "RF1 N: 9 NSET SET_LEFT_NODES-1", "RF1 N: 10 NSET SET_LEFT_NODES-1", "RF1 N: 11 NSET SET_LEFT_NODES-1", "RF1 N: 12 NSET SET_LEFT_NODES-1", "RF1 N: 13 NSET SET_LEFT_NODES-1", "RF1 N: 14 NSET SET_LEFT_NODES-1", "RF1 N: 15 NSET SET_LEFT_NODES-1", "RF1 N: 16 NSET SET_LEFT_NODES-1", "RF1 N: 17 NSET SET_LEFT_NODES-1", "RF1 N: 18 NSET SET_LEFT_NODES-1", "RF1 N: 19 NSET SET_LEFT_NODES-1", "RF1 N: 20 NSET SET_LEFT_NODES-1", "RF1 N: 21 NSET SET_LEFT_NODES-1", "RF1 N: 22 NSET SET_LEFT_NODES-1", "RF1 N: 23 NSET SET_LEFT_NODES-1", "RF1 N: 24 NSET SET_LEFT_NODES-1", "RF1 N: 25 NSET SET_LEFT_NODES-1" ) )')
tmpName = xy26.name
session.xyDataObjects.changeKey(tmpName, 'RF_total')
xy1 = session.xyDataObjects['U1 N: 513 NSET SET_RIGHT_NODES-1']
xy2 = session.xyDataObjects['RF_total']
xy3 = combine(xy1, xy2)
xyp = session.xyPlots['XYPlot-1']
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
c1 = session.Curve(xyData=xy3)
chart.setValues(curvesToPlot=(c1, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
xyp = session.xyPlots['XYPlot-1']
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
xy1 = session.xyDataObjects['U1 N: 513 NSET SET_RIGHT_NODES-1']
c1 = session.Curve(xyData=xy1)
chart.setValues(curvesToPlot=(c1, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
mdb.jobs['mono_ep_test'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "mono_ep_test.inp".
xyp = session.xyPlots['XYPlot-1']
session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
o1 = session.openOdb(
    name='D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test_fix.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
#: Model: D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test_fix.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       5
#: Number of Node Sets:          7
#: Number of Steps:              1
del session.xyDataObjects['RF1 N: 1 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 2 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 3 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 4 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 5 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 6 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 7 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 8 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 9 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 10 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 11 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 12 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 13 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 14 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 15 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 16 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 17 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 18 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 19 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 20 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 21 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 22 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 23 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 24 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF1 N: 25 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 1 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 2 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 3 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 4 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 5 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 6 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 7 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 8 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 9 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 10 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 11 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 12 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 13 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 14 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 15 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 16 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 17 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 18 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 19 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 20 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 21 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 22 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 23 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 24 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RFMAG N: 25 NSET SET_LEFT_NODES-1']
del session.xyDataObjects['RF_total']
del session.xyDataObjects['U1 N: 501 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 502 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 503 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 504 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 505 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 506 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 507 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 508 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 509 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 510 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 511 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 512 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 513 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 514 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 515 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 516 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 517 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 518 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 519 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 520 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 521 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 522 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 523 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 524 NSET SET_RIGHT_NODES-1']
del session.xyDataObjects['U1 N: 525 NSET SET_RIGHT_NODES-1']
odb = session.odbs['D:/TUBAF/Master_Thesis/Abaqus_trial/one_cycle_run/mono_ep_test_fix.odb']
xy1 = xyPlot.XYDataFromHistory(odb=odb, 
    outputVariableName='Spatial displacement: U1 at Node 13 in NSET SET_RIGHT_NODES', 
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
c1 = session.Curve(xyData=xy1)
xyp = session.xyPlots['XYPlot-1']
chartName = xyp.charts.keys()[0]
chart = xyp.charts[chartName]
chart.setValues(curvesToPlot=(c1, ), )
session.charts[chartName].autoColor(lines=True, symbols=True)
session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
