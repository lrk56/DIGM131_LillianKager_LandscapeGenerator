"""main.py
Entry point for the Maya landscape generator.
Calls build_landscape() to coordinate all geometry and material modules
and produce a full test scene in the viewport.
"""
#This file wires everything up and runs the demo scene
import sys
import os
import random

#add the project directory to sys.path so all local modules can be found
sys.path.insert(0, os.path.dirname(__file__))

from terrain_generator import create_terrain
from terrain_materials import create_terrain_material, assign_terrain_material
from oak_tree_geometry import create_trunk as oak_trunk, create_leaves as oak_leaves, create_base as oak_base
from pine_tree_geometry import create_trunk as pine_trunk, create_foliage as pine_foliage, create_base as pine_base
from tree_materials import create_material, assign_material

#Data-driven configuration (Week 7)
#A list of element dictionaries; adding a new object is just adding a dict here.
SCENE_CONFIG = [
    #one terrain
    {"type": "terrain", "plane_size": 40, "subdivs": 60, "height_scale": 4.0, "noise_scale": 0.1, "seed": 42, "name": "landscape"},
    #a few oaks with small variation
    {"type": "oak", "width": 1.0, "height": 5, "density": 20, "style": "round", "spread": 2.5},
    {"type": "oak", "width": 0.8, "height": 4.5, "density": 16, "style": "round", "spread": 2.0},
    {"type": "oak", "width": 1.2, "height": 6, "density": 24, "style": "round", "spread": 3.0},
    #a few pines
    {"type": "pine", "width": 0.4, "height": 7, "tiers": 5, "base_radius": 2.5},
    {"type": "pine", "width": 0.35, "height": 6.0, "tiers": 4, "base_radius": 2.0},
    {"type": "pine", "width": 0.5, "height": 8.0, "tiers": 6, "base_radius": 3.0},
    {"type": "pine", "width": 0.45, "height": 7.5, "tiers": 5, "base_radius": 2.7},
]

#Simple DEBUG flag for verbose builder tracing
DEBUG = False


def _build_terrain_element(**params):
    try:
        t = create_terrain(**params)
        return {"type": "terrain", "terrain": t}
    except Exception as e:
        if DEBUG:
            print("_build_terrain_element failed:", e)
        return None


def _build_oak_element(**params):
    try:
        height = params.get('height', 5)
        trunk = oak_trunk(width=params.get('width', 1), height=height)
        leaves = oak_leaves(density=params.get('density', 20), style=params.get('style', 'round'), spread=params.get('spread', 2.5), trunk_height=height)
        base = oak_base(depth=params.get('depth', 1.5), radius=params.get('radius', 1.8))

        plane_size = params.get('plane_size', 40)
        limit = plane_size / 2 * 0.85
        x = random.uniform(-limit, limit)
        z = random.uniform(-limit, limit)
        import maya.cmds as cmds
        for node in [trunk, base] + leaves:
            if node:
                pos = cmds.xform(node, q=True, ws=True, t=True)
                cmds.move(pos[0] + x, pos[1], pos[2] + z, node, ws=True)

        return {"type": "oak", "trunk": trunk, "leaves": leaves, "base": base}
    except TypeError as te:
        if DEBUG:
            print("_build_oak_element bad parameters:", te)
        return None
    except Exception as e:
        if DEBUG:
            print("_build_oak_element failed:", e)
        return None

def _build_pine_element(**params):
    try:
        height = params.get('height', 7)
        trunk = pine_trunk(width=params.get('width', 0.4), height=height)
        foliage = pine_foliage(tiers=params.get('tiers', 5), base_radius=params.get('base_radius', 2.5), trunk_height=height)
        base = pine_base(depth=params.get('depth', 1.0), radius=params.get('radius', 0.8))

        plane_size = params.get('plane_size', 40)
        limit = plane_size / 2 * 0.85
        x = random.uniform(-limit, limit)
        z = random.uniform(-limit, limit)
        import maya.cmds as cmds
        for node in [trunk, base] + foliage:
            if node:
                pos = cmds.xform(node, q=True, ws=True, t=True)
                cmds.move(pos[0] + x, pos[1], pos[2] + z, node, ws=True)

        return {"type": "pine", "trunk": trunk, "foliage": foliage, "base": base}
    except TypeError as te:
        if DEBUG:
            print("_build_pine_element bad parameters:", te)
        return None
    except Exception as e:
        if DEBUG:
            print("_build_pine_element failed:", e)
        return None


#Dispatcher map from type name to builder callable
BUILDERS = {
    "terrain": _build_terrain_element,
    "oak": _build_oak_element,
    "pine": _build_pine_element,
}


def create_element(data: dict):
    """Create a scene element from a data dictionary.

    Returns the builder result dict or None on failure. Handles missing/unknown types and bad parameters.
    """
    if not isinstance(data, dict):
        if DEBUG:
            print("create_element expects a dict, got:", type(data))
        return None

    if 'type' not in data:
        print("create_element warning: data missing 'type' key:", data)
        return None

    t = data['type']
    builder = BUILDERS.get(t)
    if builder is None:
        print(f"create_element warning: unknown type '{t}'")
        return None

    params = {k: v for k, v in data.items() if k != 'type'}
    try:
        return builder(**params)
    except TypeError as te:
        print(f"create_element warning: parameter mismatch for type '{t}':", te)
        return None
    except Exception as e:
        print(f"create_element error: builder for '{t}' raised exception:", e)
        return None


def build_scene(config_list=None):
    """Driver that builds scene elements from SCENE_CONFIG (or provided list).

    Returns a list of builder results (some entries may be None if building failed).
    """
    cfg = config_list if config_list != None else SCENE_CONFIG
    results = []
    for i, entry in enumerate(cfg):
        if DEBUG:
            print(f"build_scene: creating element {i}:", entry)
        res = create_element(entry)
        if res is not None:
            t = entry.get('type')
            if t == 'terrain':
                assign_terrain_material(res['terrain'], create_terrain_material(entry.get('preset', 'grass')))
            elif t in ('oak', 'pine'):
                mat = create_material(color=(0.3, 0.5, 0.15))
                for key, p in res.items():
                    if key == 'type':
                        continue
                    if isinstance(p, list):
                        for i in p:
                            assign_material(i, mat)
                    else:
                        assign_material(p, mat)
        results.append(res)
    return results



def build_landscape():
    """
    Primary function that coordinates all geometry and material modules to generate a test scene.
    Builds a terrain with grass material, one oak tree, and one pine tree side by side.

    Returns:
        dict: A dictionary containing all created node names grouped by type.
    """
    scene = {}

    #start making the terrain
    print("Building terrain")
    terrain = create_terrain(plane_size=40, subdivs=60, height_scale=4.0, noise_scale=0.1, seed=42, name='landscape')
    terrain_mat = create_terrain_material(preset='grass')
    assign_terrain_material(terrain, terrain_mat)
    scene['terrain'] = terrain
    #terrain done
    print(f"Terrain created and assigned grass material: {terrain}")

    #now the oak, left side
    print("Building oak tree")
    #offset oak to the left of center
    oak_x = -6

    o_trunk = oak_trunk(width=1, height=5)
    o_leaves = oak_leaves(density=20, style='round', spread=2.5, trunk_height=5)
    o_base = oak_base(depth=1.5, radius=1.8)

    #move all oak parts to the left so it looks nice
    for node in [o_trunk, o_base] + o_leaves:
        pos = __import__('maya').cmds.xform(node, q=True, ws=True, t=True)
        __import__('maya').cmds.move(pos[0] + oak_x, pos[1], pos[2], node, ws=True)

    #make simple oak materials
    oak_bark_mat = create_material(color=(0.35, 0.2, 0.08))
    oak_leaf_mat = create_material(color=(0.13, 0.45, 0.1))
    assign_material(o_trunk,    oak_bark_mat)
    assign_material(o_base,     oak_bark_mat)
    #oak has leaf geometry assigned
    assign_material(o_leaves,   oak_leaf_mat)

    scene['oak'] = {'trunk': o_trunk, 'leaves': o_leaves, 'base': o_base}
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
    assign_material(p_trunk, pine_bark_mat)
    assign_material(p_base, pine_bark_mat)
    assign_material(p_foliage, pine_foliage_mat)

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