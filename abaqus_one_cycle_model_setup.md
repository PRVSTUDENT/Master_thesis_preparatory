# Abaqus/CAE 2021 — Step‑by‑Step: Build a 3D One‑Cycle Model and Generate an ODB

This guide creates the small model we used to generate a **1‑cycle ODB** for cycle‑jump demonstrations.

> Goal: produce `one-cycle.odb` quickly and reliably.

---

## 0) Set a working directory (important)
1. **File → Set Working Directory…**
2. Choose a folder, e.g.  
   `D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\`

Abaqus writes the job files (`.inp`, `.msg`, `.sta`, `.odb`, …) here.

---

## 1) Create a simple 3D block part
**Module:** Part  
1. **Part → Create…**
2. Name: `Part-1`
3. Modeling space: **3D**
4. Type: **Deformable**
5. Base feature: **Solid, Extrusion**
6. Sketch a rectangle (example dimensions):
   - corners: (0,0) to (10,2)
7. Extrude depth: `2`

You now have a \(10 \times 2 \times 2\) block.

---

## 2) Create material and assign section
**Module:** Property

### 2.1 Material
1. **Material → Create…**
2. Name: `Mat-Elastic`
3. **Mechanical → Elasticity → Elastic**
4. Example input:
   - `E = 70000`
   - `nu = 0.33`
5. OK

### 2.2 Section
1. **Section → Create…**
2. Name: `Sec-1`
3. Category: **Solid**
4. Type: **Homogeneous**
5. Select material `Mat-Elastic`
6. OK

### 2.3 Assign section
1. **Assign → Section…**
2. Region: select the whole solid (click the block) → **Done**
3. Choose section: `Sec-1` → OK

Check: Model tree shows **Section Assignments (1)** under the part.

---

## 3) Create an assembly instance (so loads/BCs work)
**Module:** Assembly  
1. **Instance → Create…**
2. Select `Part-1`
3. Choose **Dependent**
4. OK

If the model “disappears”, you are likely viewing an empty assembly. Use:
- **View → Fit View**
- confirm the instance exists in the model tree.

---

## 4) Create a one‑cycle analysis step
**Module:** Step  
1. **Step → Create…**
2. Name: `Step-1`
3. Procedure: **Static, General**
4. Time period: `1.0`  (represents one cycle duration)

### 4.1 Field output frequency (so you get many frames)
1. **Output → Field Output Requests**
2. Edit the default request (`F-Output-1`)
3. Set **Number of intervals** = 50 (or 100)
4. Ensure **S** (stress) is included (default usually includes it)

---

## 5) Create a cyclic amplitude (Periodic sine)
Periodic amplitude uses circular frequency \(\omega\) (rad/time).

For **one cycle** in a step of length \(T=1.0\):
\[
\omega = \frac{{2\pi}}{{T}} = 2\pi \approx 6.283185307
\]

**Module:** Load (or Tools menu)  
1. **Tools → Amplitude → Create…**
2. Name: `Amp-1`
3. Type: **Periodic**
4. Enter:
   - Circular frequency: `6.283185307`
   - Starting time: `0.0`
   - Initial amplitude: `0.0`
5. OK

(Alternative: use a **Tabular** amplitude with 5 points if you prefer a piecewise linear cycle.)

---

## 6) Apply boundary conditions (displacement controlled)
**Module:** Load

### 6.1 Fix left face
1. **BC → Create…**
2. Name: `BC-Left`
3. Step: **Initial**
4. Type: **Displacement/Rotation**
5. Select the face at **x = 0**
6. Set: `U1=0, U2=0, U3=0`
7. OK

### 6.2 Apply cyclic displacement on right face
1. **BC → Create…**
2. Name: `BC-Right`
3. Step: `Step-1`
4. Type: **Displacement/Rotation**
5. Select the face at **x = 10**
6. Set only: `U1 = 0.1`  (example)
   - Leave `U2`, `U3` **UNSET** (free)
7. Click **Amplitude…** → select `Amp-1`
8. OK

---

## 7) Mesh the part
**Module:** Mesh  
1. Ensure you are meshing the **Part**, not the Assembly:
   - double‑click `Part-1` under **Parts** to display it.
2. **Seed → Part**
   - Global size: `0.5` (or `1.0` for faster)
3. **Element Type**
   - Choose: **C3D8R**
4. **Mesh → Part**

---

## 8) Create and run the job (creates the ODB)
**Module:** Job  
1. **Job → Create…**
2. Name: `one-cycle`
3. Model: `Model-1`
4. OK
5. **Job → Manager…**
6. Select `one-cycle` → **Submit**
7. Wait for **Status: Completed**

In the working directory you should see:
- `one-cycle.odb`  ✅

---

## 9) Open the ODB (optional check)
**Module:** Visualization  
1. **File → Open…**
2. Select `one-cycle.odb`
3. Plot `S` or `S11` over frames.

---

## 10) Notes / troubleshooting
- If Abaqus says “cannot continue yet…”, press **Esc** to cancel any ongoing selection tool.
- If the model disappears after switching modules, ensure the **Assembly instance** exists and use **Fit View**.
- If scripts complain about missing sets (e.g., `EALL`), either:
  - create an element set in the Assembly (Tools → Set → Create), or
  - use the **NOSET** scripts that scan the whole model.
