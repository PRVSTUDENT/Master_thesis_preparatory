# Abaqus/CAE Python script
# Rebuilds the monotonic elastic-plastic bar model used in Phase 1.
# Creates geometry, material, mesh, BCs, history outputs, and a job.
# Intended to run with:
#   abaqus cae noGUI=rebuild_one_cycle_model.py
# or from Abaqus/CAE: File -> Run Script

from abaqus import *
from abaqusConstants import *
import regionToolset
import mesh
import os

# -----------------------------
# User settings
# -----------------------------
MODEL_NAME = 'Model-1'
PART_NAME = 'Part-1'
MATERIAL_NAME = 'Steel_EP'
SECTION_NAME = 'Sec_EP'
JOB_NAME = 'mono_ep_test'

# Geometry in mm
LENGTH = 10.0
HEIGHT = 2.0
DEPTH = 2.0

# Material in MPa-mm system
E = 210000.0
NU = 0.30
PLASTIC_TABLE = (
    (250.0, 0.0),
    (300.0, 0.02),
    (350.0, 0.10),
)

# Mesh
GLOBAL_SEED = 0.5

# Loading
RIGHT_FACE_U1 = 0.5

# Output files
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    BASE_DIR = os.getcwd()
CAE_PATH = os.path.join(BASE_DIR, 'one_cycle_rebuilt.cae')

# -----------------------------
# Fresh model database
# -----------------------------
Mdb()
if MODEL_NAME != 'Model-1' and 'Model-1' in mdb.models.keys():
    del mdb.models['Model-1']
model = mdb.models[MODEL_NAME]

# -----------------------------
# Geometry
# -----------------------------
sk = model.ConstrainedSketch(name='__profile__', sheetSize=50.0)
sk.rectangle(point1=(0.0, 0.0), point2=(LENGTH, HEIGHT))
part = model.Part(name=PART_NAME, dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sk, depth=DEPTH)
del model.sketches['__profile__']

# -----------------------------
# Material + section
# -----------------------------
mat = model.Material(name=MATERIAL_NAME)
mat.Elastic(table=((E, NU),))
mat.Plastic(table=PLASTIC_TABLE)
model.HomogeneousSolidSection(name=SECTION_NAME, material=MATERIAL_NAME, thickness=None)

cells = part.cells[:]
region_cells = regionToolset.Region(cells=cells)
part.SectionAssignment(region=region_cells, sectionName=SECTION_NAME, offset=0.0,
                       offsetType=MIDDLE_SURFACE, offsetField='',
                       thicknessAssignment=FROM_SECTION)

# -----------------------------
# Mesh
# -----------------------------
part.seedPart(size=GLOBAL_SEED, deviationFactor=0.1, minSizeFactor=0.1)
part.setMeshControls(regions=part.cells[:], elemShape=HEX, technique=STRUCTURED)
elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD,
                          secondOrderAccuracy=OFF, hourglassControl=DEFAULT,
                          distortionControl=DEFAULT)
part.setElementType(regions=(part.cells[:],), elemTypes=(elemType1,))
part.generateMesh()

# -----------------------------
# Assembly
# -----------------------------
a = model.rootAssembly
a.DatumCsysByDefault(CARTESIAN)
inst = a.Instance(name=PART_NAME + '-1', part=part, dependent=ON)

# Face regions for BCs
left_face = inst.faces.findAt(((0.0, HEIGHT/2.0, DEPTH/2.0),))
right_face = inst.faces.findAt(((LENGTH, HEIGHT/2.0, DEPTH/2.0),))

a.Set(name='Set-1', faces=left_face)
a.Set(name='Set-2', faces=right_face)

# Node sets for history output (carefully named and on correct faces)
tol = 1.0e-8
left_nodes = inst.nodes.getByBoundingBox(xMin=-tol, xMax=tol,
                                         yMin=-tol, yMax=HEIGHT+tol,
                                         zMin=-tol, zMax=DEPTH+tol)
right_nodes = inst.nodes.getByBoundingBox(xMin=LENGTH-tol, xMax=LENGTH+tol,
                                          yMin=-tol, yMax=HEIGHT+tol,
                                          zMin=-tol, zMax=DEPTH+tol)
a.Set(name='Set_Left_Nodes', nodes=left_nodes)
a.Set(name='Set_Right_Nodes', nodes=right_nodes)

# -----------------------------
# Step
# -----------------------------
model.StaticStep(name='Step-1', previous='Initial', timePeriod=1.0,
                 maxNumInc=100, initialInc=0.1, minInc=1e-5, maxInc=0.1,
                 nlgeom=OFF)

# -----------------------------
# Boundary conditions
# -----------------------------
model.DisplacementBC(name='BC-left', createStepName='Step-1',
                     region=a.sets['Set-1'], u1=0.0, u2=0.0, u3=0.0,
                     ur1=UNSET, ur2=UNSET, ur3=UNSET,
                     amplitude=UNSET, fixed=OFF, distributionType=UNIFORM,
                     fieldName='', localCsys=None)

model.DisplacementBC(name='BC-right', createStepName='Step-1',
                     region=a.sets['Set-2'], u1=RIGHT_FACE_U1, u2=UNSET, u3=UNSET,
                     ur1=UNSET, ur2=UNSET, ur3=UNSET,
                     amplitude=UNSET, fixed=OFF, distributionType=UNIFORM,
                     fieldName='', localCsys=None)

# -----------------------------
# Output requests
# -----------------------------
# Keep default field output, but make sure PEEQ is requested.
try:
    field_req = model.fieldOutputRequests['F-Output-1']
    field_req.setValues(variables=('S', 'E', 'U', 'RF', 'PE', 'PEEQ'))
except Exception:
    # Some Abaqus versions expose different model APIs in noGUI mode.
    # Continue with defaults; history outputs below are the critical part.
    pass

# Remove default history output and add clean set-based requests.
try:
    for key in list(model.historyOutputRequests.keys()):
        del model.historyOutputRequests[key]
except Exception:
    pass

try:
    model.HistoryOutputRequest(name='H-RF-left', createStepName='Step-1',
                               variables=('RF1',), region=a.sets['Set_Left_Nodes'],
                               sectionPoints=DEFAULT, rebar=EXCLUDE)
    model.HistoryOutputRequest(name='H-U-right', createStepName='Step-1',
                               variables=('U1',), region=a.sets['Set_Right_Nodes'],
                               sectionPoints=DEFAULT, rebar=EXCLUDE)
except Exception:
    pass

# -----------------------------
# Job
# -----------------------------
job = mdb.Job(name=JOB_NAME, model=MODEL_NAME, description='Monotonic elastic-plastic sanity test',
              type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
              memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
              explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE,
              echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
              userSubroutine='', scratch='', resultsFormat=ODB,
              multiprocessingMode=DEFAULT, numCpus=1, numDomains=1, numGPUs=0)

# Write input file for convenience.
job.writeInput(consistencyChecking=OFF)

# Save CAE database.
mdb.saveAs(pathName=CAE_PATH)

print('Rebuilt model successfully.')
print('CAE saved to:', CAE_PATH)
print('Input written to:', os.path.join(BASE_DIR, JOB_NAME + '.inp'))
