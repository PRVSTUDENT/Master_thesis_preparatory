# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2024 replay file
# Internal Version: 2023_09_21-14.55.25 RELr426 190762
# Run by pruth on Mon Apr 20 06:04:47 2026
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
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
#--- Recover file: 'abaqus1.rec' ---
# -*- coding: mbcs -*- 
from mesh import *
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
    point2=(10.0, 2.0))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-1', 
    type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-1'].BaseSolidExtrude(depth=2.0, 
    sketch=mdb.models['Model-1'].sketches['__profile__'])
del mdb.models['Model-1'].sketches['__profile__']
mdb.models['Model-1'].Material(name='Steel_EP')
mdb.models['Model-1'].materials['Steel_EP'].Elastic(table=((210000.0, 0.3), ))
mdb.models['Model-1'].materials['Steel_EP'].Plastic(table=((250.0, 0.0), (
    300.0, 0.02), (350.0, 0.1)))
mdb.models['Model-1'].HomogeneousSolidSection(material='Steel_EP', 
    name='Sec_EP', thickness=None)
mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(
    mask=('[#1 ]', ), )), sectionName='Sec_EP', 
    thicknessAssignment=FROM_SECTION)
mdb.models['Model-1'].parts['Part-1'].seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size=0.5)
mdb.models['Model-1'].parts['Part-1'].setMeshControls(elemShape=HEX, 
    regions=mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(
    mask=('[#1 ]', ), ), technique=STRUCTURED)
mdb.models['Model-1'].parts['Part-1'].setElementType(elemTypes=(ElemType(
    elemCode=C3D8R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, 
    hourglassControl=DEFAULT, distortionControl=DEFAULT), ), regions=(
    mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(mask=(
    '[#1 ]', ), ), ))
mdb.models['Model-1'].parts['Part-1'].generateMesh()
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-1-1', 
    part=mdb.models['Model-1'].parts['Part-1'])
mdb.models['Model-1'].rootAssembly.Set(
    faces=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
    mask=('[#1 ]', ), ), name='Set-1')
mdb.models['Model-1'].rootAssembly.Set(
    faces=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
    mask=('[#4 ]', ), ), name='Set-2')
mdb.models['Model-1'].rootAssembly.Set(name='Set_Left_Nodes', 
    nodes=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].nodes.getSequenceFromMask(
    mask=('[#0:15 #fff00000 #1fff ]', ), ))
mdb.models['Model-1'].rootAssembly.Set(name='Set_Right_Nodes', 
    nodes=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].nodes.getSequenceFromMask(
    mask=('[#1ffffff ]', ), ))
mdb.models['Model-1'].StaticStep(initialInc=0.1, maxInc=0.1, maxNumInc=100, 
    minInc=1e-05, name='Step-1', nlgeom=OFF, previous='Initial', 
    timePeriod=1.0)
mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, 
    name='BC-left', region=mdb.models['Model-1'].rootAssembly.sets['Set-1'], 
    u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET)
#--- End of Recover file ------
