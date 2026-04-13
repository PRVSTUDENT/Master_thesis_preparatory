# Run with: abaqus cae noGUI=scripts/build_model.py
"""
build_model.py
==============
Reads a JSON parameter file and builds an Abaqus/CAE model for cyclic-jump
fatigue analyses.  Writes an Abaqus input file (.inp) to the models/ folder.

Usage
-----
    abaqus cae noGUI=scripts/build_model.py

The script looks for a parameter file at:
    models/cyclic_jump_parameters.json

Edit that file to change material properties, geometry, loading, or mesh
settings before running.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Locate the repository root regardless of the working directory
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "models")
PARAM_FILE = os.path.join(MODELS_DIR, "cyclic_jump_parameters.json")
JOB_NAME = "cyclic_jump_v1"


def load_parameters(param_file):
    """Return the parameter dictionary from the JSON file."""
    with open(param_file, "r") as fh:
        return json.load(fh)


def build_model(params):
    """
    Create an Abaqus/CAE model using the supplied parameters.

    This function uses the Abaqus scripting interface (only available when
    running inside ``abaqus cae noGUI=...``).
    """
    # Lazy import so the module can be parsed without Abaqus installed
    import part        # noqa: F401  (Abaqus kernel module)
    import material    # noqa: F401
    import section     # noqa: F401
    import assembly    # noqa: F401
    import step        # noqa: F401
    import load        # noqa: F401
    import mesh        # noqa: F401
    from abaqus import mdb, session  # noqa: F401

    mat = params["material"]
    geo = params["geometry"]
    lod = params["loading"]
    msh = params["mesh"]

    model_name = JOB_NAME
    m = mdb.Model(name=model_name)

    # --- Geometry -----------------------------------------------------------
    s = m.ConstrainedSketch(name="profile", sheetSize=200.0)
    s.rectangle(
        point1=(0.0, 0.0),
        point2=(geo["width"], geo["height"]),
    )
    p = m.Part(name="Specimen", dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s, depth=geo["depth"])

    # --- Material -----------------------------------------------------------
    mat_obj = m.Material(name="Steel")
    mat_obj.Elastic(table=((mat["E"], mat["nu"]),))
    mat_obj.Plastic(table=((mat["sig_y"], 0.0),))

    # --- Section & assignment -----------------------------------------------
    m.HomogeneousSolidSection(name="SecSpecimen", material="Steel", thickness=None)
    region = p.Set(cells=p.cells, name="AllCells")
    p.SectionAssignment(region=region, sectionName="SecSpecimen")

    # --- Assembly -----------------------------------------------------------
    a = m.rootAssembly
    inst = a.Instance(name="Specimen-1", part=p, dependent=ON)

    # --- Step ---------------------------------------------------------------
    m.StaticStep(
        name="Step-1",
        previous="Initial",
        maxNumInc=10000,
        initialInc=0.01,
        minInc=1e-6,
        maxInc=0.1,
        nlgeom=ON,
    )

    # --- Boundary conditions ------------------------------------------------
    bottom_face = inst.faces.findAt(((geo["width"] / 2.0, 0.0, geo["depth"] / 2.0),))
    bottom_region = a.Set(faces=bottom_face, name="BOTTOM")
    m.EncastreBC(name="Fixed", createStepName="Initial", region=bottom_region)

    top_face = inst.faces.findAt(
        ((geo["width"] / 2.0, geo["height"], geo["depth"] / 2.0),)
    )
    top_region = a.Set(faces=top_face, name="LOAD_FACE")
    m.DisplacementBC(
        name="CyclicLoad",
        createStepName="Step-1",
        region=top_region,
        u2=lod["amplitude"],
    )

    # --- History output (force & displacement) ------------------------------
    top_node_set = a.Set(
        nodes=inst.nodes.getByBoundingBox(
            xMin=0, yMin=geo["height"] - 0.01, zMin=0,
            xMax=geo["width"], yMax=geo["height"] + 0.01, zMax=geo["depth"],
        ),
        name="LOAD_NODE",
    )
    m.HistoryOutputRequest(
        name="FD_Output",
        createStepName="Step-1",
        variables=("RF2", "U2"),
        region=top_node_set,
        frequency=1,
    )

    # --- Mesh ---------------------------------------------------------------
    p.seedPart(size=msh["global_seed"], deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

    # --- Write input file ---------------------------------------------------
    inp_path = os.path.join(MODELS_DIR, JOB_NAME + ".inp")
    mdb.jobs[model_name] = mdb.Job(name=model_name, model=model_name)
    mdb.jobs[model_name].writeInput(consistencyChecking=OFF)

    # Abaqus writes the .inp next to the working directory; move if needed
    local_inp = JOB_NAME + ".inp"
    if os.path.exists(local_inp) and local_inp != inp_path:
        import shutil
        shutil.move(local_inp, inp_path)

    print("Input file written to: {}".format(inp_path))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(PARAM_FILE):
        sys.exit(
            "Parameter file not found: {}\n"
            "Copy and edit models/cyclic_jump_parameters.json before running.".format(
                PARAM_FILE
            )
        )

    params = load_parameters(PARAM_FILE)
    build_model(params)
