# DIGM131_LillianKager_LandscapeGenerator
## What it Does

This is a Maya tool that generates a landscape from configuration parameters. 
The user can control tree density, landscape altidude characteristics, terrain material, 
and snowcover without touching the creation logic. 

## Planned Features
- [x] Core geometry functions (Week 6)
- [ ] Data-driven configuration (Week 7)
- [ ] Error handling + debug mode (Week 8)
- [ ] Maya UI window + JSON save/load (Week 9)
- [ ] Polish + documentation (Week 10)

## Project Structure
```
LandscapeGenerator/
    tree_geometry.py       # create_trunk, create_branches, create_leaves, create_roots 
    tree_materials.py      # create_material, assign_material
    perlin_terrain.py      # ...
    terrain_materials.py   # create_material, assign_material 
    main.py                # Entry point, config, build_landscape()
    README.md              # This file
```

## Functions
### tree_geometry.py
- `create_trunk(width, height)` — It creates the trunk of a tree. 
- `create_branches(count, spread)` — Generates branch structures relative to the trunk.
- `create_leaves(density, style)` — Populates the branches with foliage geometry.
- `create_roots(depth, radius)` — Generates above-ground root structures.

## DIGM131_LillianKager_LandscapeGenerator

This repository contains a small set of helper modules that generate a stylized landscape inside Autodesk Maya. The code builds a terrain mesh displaced with Perlin-style fractal noise, plus a couple of tree types (oak and pine). Materials are created and assigned with helper utilities.

This README documents every public function in the project, their parameters and return values, basic usage, and troubleshooting notes so you can run and extend the tool inside Maya.

---

## Quick start (inside Maya)

1. Open Autodesk Maya.
2. Make sure the folder containing this project is on Maya's Python path, or copy the files into your Maya scripts folder.
3. Open the Script Editor and run / source `main.py` or call `build_landscape()` from the Python tab.

Example (Python tab):

```python
from main import build_landscape
scene = build_landscape()
```

The function returns a dictionary describing created scene nodes.

---

## Project layout (files and purpose)

- `main.py` — entry point and scene builder (calls geometry and material helpers to create a test scene).
- `terrain_generator.py` — helper that creates a subdivided plane and displaces vertices with fractal Perlin noise.
- `demo_perlin.py` — a small Perlin-like noise implementation used by the terrain generator.
- `terrain_materials.py` — terrain shader presets (grass, sand, stone) and helper to assign them.
- `oak_tree_geometry.py` — builders for oak-style tree geometry: trunk, branches, leaves, base.
- `pine_tree_geometry.py` — builders for pine-style tree geometry: trunk, stacked foliage cones, base.
- `tree_materials.py` — simple lambert shader creation and assignment helpers for tree parts.

---

### main.py

- build_landscape()
    - Coordinates terrain and tree creation to produce a simple test scene.
    - Returns: dict with keys `terrain`, `oak`, `pine`. `terrain` is the terrain transform name. `oak` and `pine` are nested dicts describing created parts.
    - Behavior: Creates a terrain (via `terrain_generator.create_terrain`), an oak tree (trunk, branches, leaves, base), and a pine tree (trunk, stacked foliage cones, base). Assigns materials using the material helpers.

### terrain_generator.py

- create_terrain(plane_size=20, subdivs=50, height_scale=5.0, noise_scale=0.15, octaves=4, persistence=0.5, lacunarity=2.0, seed=42, name='terrain') -> str
    - Creates a subdivided poly plane and displaces each vertex along Y using fractal noise from `demo_perlin.PerlinNoise`.
    - Parameters:
        - plane_size (float): Width and height of the created plane in world units.
        - subdivs (int): Number of subdivisions along each axis (sets `sx` and `sy` for `polyPlane`).
        - height_scale (float): Scales the noise output to control maximum vertical displacement.
        - noise_scale (float): Input scale for the noise function; lower values create broader hills.
        - octaves (int): Number of fractal octaves.
        - persistence (float): Amplitude multiplier per octave.
        - lacunarity (float): Frequency multiplier per octave.
        - seed (int): Random seed used by the `PerlinNoise` instance for deterministic results.
        - name (str): Name for the created plane transform.
    - Returns: The transform node name of the created plane (string).

Notes: The function uses `cmds.polyEvaluate(..., vertex=True)` and iterates every vertex to call `cmds.pointPosition` and `cmds.xform` to displace vertices.

### terrain_materials.py

- create_terrain_material(preset='grass', color=None, ambience=None, diffuse=None) -> str
    - Creates a lambert shader with a shading group and applies preset properties for color, ambient color, and diffuse intensity.
    - Parameters:
        - preset (str): One of the available presets: `'grass'`, `'sand'`, `'stone'`.
        - color (tuple of 3 floats or None): Optional override for the main shader color (R,G,B values 0..1).
        - ambience (tuple of 3 floats or None): Optional override for ambient color.
        - diffuse (float or None): Optional override of the diffuse intensity.
    - Returns: Shader node name (string).

- assign_terrain_material(terrain, material) -> str
    - Assigns a shader to the given terrain transform using the material's shading group.
    - Parameters:
        - terrain (str): Transform node of the terrain mesh.
        - material (str): Shader node name created by `create_terrain_material`.
    - Returns: Shading group node name used to assign the material.

### oak_tree_geometry.py

- create_trunk(width=1, height=5) -> str
    - Builds a `polyCylinder`, moves it to sit on the ground (translates by height/2) and returns its transform name.
    - Parameters:
        - width (float): Diameter of the trunk.
        - height (float): Height of the trunk.

- create_branches(count=5, spread=3, trunk_height=5) -> list[str]
    - Creates `count` short cylinders rotated and moved to simulate branches fanning out from the top of the trunk.
    - Parameters:
        - count (int): Number of branches to create.
        - spread (float): Length/height of each branch cylinder.
        - trunk_height (float): Y position to place the branches (usually trunk height).
    - Returns: List of branch transform node names.

- create_leaves(density=20, style='round', spread=2.5, trunk_height=5) -> list[str]
    - Creates `density` poly spheres scattered around treetop to emulate a leafy canopy.
    - Parameters:
        - density (int): Number of leaf spheres.
        - style (str): `'round'` (default) or `'pointy'` — the latter scales spheres vertically to appear pointier.
        - spread (float): Scatter radius for foliage placement.
        - trunk_height (float): Base Y position for foliage.
    - Returns: List of leaf transform node names.

- create_base(depth=1.5, radius=1.8) -> str
    - Creates a cone at the base of the trunk to simulate a flared root area and returns the transform node name.

### pine_tree_geometry.py

- create_trunk(width=0.4, height=7) -> str
    - Creates a tapered cylinder for the pine trunk and moves it so the trunk sits on ground.
    - Parameters:
        - width (float): Base diameter.
        - height (float): Height of the trunk.

- create_foliage(tiers=5, base_radius=2.5, trunk_height=7) -> list[str]
    - Generates stacked cones (one per tier) that form the conical silhouette of a pine tree.
    - Parameters:
        - tiers (int): Number of cone layers.
        - base_radius (float): Radius of the largest (bottom) cone.
        - trunk_height (float): Height of the trunk to offset cones vertically.
    - Returns: List of cone transform node names (from bottom to top).

- create_base(depth=1.0, radius=0.8) -> str
    - Small cone at base to ground the pine tree.

### tree_materials.py

- create_material(color=(0.4, 0.25, 0.1), texture_path=None) -> str
    - Creates a lambert shader and optionally connects a file texture node.
    - Parameters:
        - color (tuple): RGB float values 0..1 used when no `texture_path` is supplied.
        - texture_path (str or None): File path to a texture image. If set, a `file` node is created and connected to the shader color.
    - Returns: Shader node name (string).

- assign_material(obj, material) -> str
    - Assigns an existing shader to a Maya transform or list of transforms.
    - Parameters:
        - obj (str or list[str]): Transform node name(s) to assign the shader to.
        - material (str): Shader node name.
    - Returns: Shading group node name used for the assignment.

---

## Author

Lillian Kager | lrk56 | DIGM 131 | Drexel University

