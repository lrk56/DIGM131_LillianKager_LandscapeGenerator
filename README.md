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
    main.py                # Entry point, config, build_landscape()
    README.md              # This file
```

## Functions
### tree_geometry.py
- `create_trunk(width, height)` — It creates the trunk of a tree. 
- `create_branches(count, spread)` — Generates branch structures relative to the trunk.
- `create_leaves(density, style)` — Populates the branches with foliage geometry.
- `create_roots(depth, radius)` — Generates above-ground root structures.

### tree_materials.py
- `create_material(color, texture_path)` — Defines a new shader or material for tree parts.
- `assign_material(object, material)` — Maps specific materials to trunk or leaf geometry.

### main.py
- `build_landscape()` — The primary loop that coordinates geometry and material functions to generate the scene.

## How to Run 
1. Open Maya
2. Open Script Editor (Windows > General Editors > Script Editor)
3. Source `main.py` from the LandscapeGenerator folder

## Author
Lillian Kager | DIGM 131 | Drexel University

