"""main.py
Entry point for the Maya landscape generator.
Calls build_landscape() to coordinate all geometry and material modules
and produce a full test scene in the viewport.
"""
#This file wires everything up and runs the demo scene
import sys
import os

#add the project directory to sys.path so all local modules can be found
sys.path.insert(0, os.path.dirname(__file__))

from terrain_generator import create_terrain
from terrain_materials import create_terrain_material, assign_terrain_material
from oak_tree_geometry import create_trunk as oak_trunk, create_branches as oak_branches, create_leaves as oak_leaves, create_base as oak_base
from pine_tree_geometry import create_trunk as pine_trunk, create_foliage as pine_foliage, create_base as pine_base
from tree_materials import create_material, assign_material


def build_landscape():
    """
    Primary function that coordinates all geometry and material modules to generate a test scene.
    Builds a terrain with grass material, one oak tree, and one pine tree side by side.

    Returns:
        dict: A dictionary containing all created node names grouped by type.
    """
    scene = {}

    #start making the terrain
    print("--- Building terrain ---")
    terrain = create_terrain(plane_size=40, subdivs=60, height_scale=4.0, noise_scale=0.1, seed=42, name='landscape')
    terrain_mat = create_terrain_material(preset='grass')
    assign_terrain_material(terrain, terrain_mat)
    scene['terrain'] = terrain
    #terrain done
    print(f"Terrain created and assigned grass material: {terrain}")

    #now the oak, left side
    print("--- Building oak tree ---")
    #offset oak to the left of center
    oak_x = -6

    o_trunk = oak_trunk(width=1, height=5)
    o_branches = oak_branches(count=5, spread=3, trunk_height=5)
    o_leaves = oak_leaves(density=20, style='round', spread=2.5, trunk_height=5)
    o_base = oak_base(depth=1.5, radius=1.8)

    #move all oak parts to the left so it looks nice
    for node in [o_trunk, o_base] + o_branches + o_leaves:
        pos = __import__('maya').cmds.xform(node, q=True, ws=True, t=True)
        __import__('maya').cmds.move(pos[0] + oak_x, pos[1], pos[2], node, ws=True)

    #make simple oak materials
    oak_bark_mat = create_material(color=(0.35, 0.2, 0.08))
    oak_leaf_mat = create_material(color=(0.13, 0.45, 0.1))
    assign_material(o_trunk,    oak_bark_mat)
    assign_material(o_base,     oak_bark_mat)
    assign_material(o_branches, oak_bark_mat)
    assign_material(o_leaves,   oak_leaf_mat)

    scene['oak'] = {'trunk': o_trunk, 'branches': o_branches, 'leaves': o_leaves, 'base': o_base}
    #oak done
    print(f"Oak tree created at x={oak_x}")

    #pine tree to the right
    print("Building pine tree")
    #offset pine to the right of center
    pine_x = 6

    p_trunk = pine_trunk(width=0.4, height=7)
    p_foliage = pine_foliage(tiers=5, base_radius=2.5, trunk_height=7)
    p_base = pine_base(depth=1.0, radius=0.8)

    #move all pine parts to the right so they don't overlap the oak
    from maya import cmds
    for node in [p_trunk, p_base] + p_foliage:
        pos = cmds.xform(node, q=True, ws=True, t=True)
        cmds.move(pos[0] + pine_x, pos[1], pos[2], node, ws=True)

    #pine materials are simple too
    pine_bark_mat = create_material(color=(0.25, 0.15, 0.08))
    pine_foliage_mat = create_material(color=(0.08, 0.3, 0.1))
    assign_material(p_trunk,    pine_bark_mat)
    assign_material(p_base,     pine_bark_mat)
    assign_material(p_foliage,  pine_foliage_mat)

    scene['pine'] = {'trunk': p_trunk, 'foliage': p_foliage, 'base': p_base}
    #pine done
    print(f"Pine tree created at x={pine_x}")

    print("--- Scene build complete ---")
    return scene


if __name__ == "__main__":
    scene = build_landscape()

    print("\nScene summary:")
    print(f"  Terrain:     {scene['terrain']}")
    print(f"  Oak trunk:   {scene['oak']['trunk']}")
    print(f"  Oak leaves:  {len(scene['oak']['leaves'])} spheres")
    print(f"  Pine trunk:  {scene['pine']['trunk']}")
    print(f"  Pine tiers:  {len(scene['pine']['foliage'])} cones")