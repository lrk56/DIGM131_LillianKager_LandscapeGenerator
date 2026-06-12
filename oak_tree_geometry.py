"""oak_tree_geometry.py
Utility module for generating a stylized oak tree in Autodesk Maya.
Contains builder functions for trunk, foliage, and base geometry.
"""
from maya import cmds
import random
import math

#DEBUG flag - when True builder functions will print parameters and errors
DEBUG = False


def create_trunk(width=1, height=5):
    """
    Creates a cylindrical trunk mesh centered at the world origin.

    Args:
        width (float): Diameter of the trunk. Defaults to 1.
        height (float): Height of the trunk. Defaults to 5.

    Returns:
        str: Name of the created trunk transform node.
    """
    #input validation
    if width <= 0:
        if DEBUG: print('create_trunk: invalid width, using default 1')
        width = 1
    if height <= 0:
        if DEBUG: print('create_trunk: invalid height, using default 5')
        height = 5

    try:
        trunk = cmds.polyCylinder(h=height, r=width/2, sx=8, sy=1, sz=1)[0]
        #move trunk so it sits on the ground
        cmds.move(0, height/2, 0, trunk)
        return trunk
    except Exception as e:
        if DEBUG: print('create_trunk failed:', e)
        return None

#oak uses foliage spheres (no branch primitives)

def create_leaves(density=20, style='round', spread=2.5, trunk_height=5):
    """
    Creates large overlapping spheres clustered at the treetop to simulate foliage.
    Arguments:
        density (int): Number of leaf spheres to generate. Defaults to 20.
        style (str): Leaf shape style, 'round' or 'pointy'. Defaults to 'round'.
        spread (float): Horizontal and vertical scatter radius of the canopy. Defaults to 2.5.
        trunk_height (float): Y position of the trunk top to anchor teh foliage. Defaults to 5.

    Returns:
        list[str]: List of leaf sphere transform node names.
    """
    leaves = []
    if density <= 0:
        if DEBUG: print('create_leaves: invalid density, using default 20')
        density = 20
    try:
        for i in range(density):
            r = random.uniform(0.8, 1.5)
            leaf = cmds.polySphere(r=r, sx=8, sy=8)[0]
            #scatter leaf spheres in a canopy above the trunk
            x = random.uniform(-spread, spread)
            z = random.uniform(-spread, spread)
            y = trunk_height + random.uniform(0, spread * 0.8)
            cmds.move(x, y, z, leaf)

            if style == 'pointy':
                cmds.scale(0.5, 1.5, 0.5, leaf)

            leaves.append(leaf)
        return leaves
    except Exception as e:
        if DEBUG: print('create_leaves failed:', e)
        return []


def create_base(depth=1.5, radius=1.8):
    """
    Creates a cone at the base of the trunk to simulate a flared root structure.

    Args:
        depth (float): Height of the base cone. Defaults to 1.5.
        radius (float): Radius of the cone base. Defaults to 1.8.

    Returns:
        str: Name of the created base cone transform node.
    """
    base = cmds.polyCone(h=depth, r=radius, sx=8, sy=1)[0]
    #small cone to sit under the trunk
    cmds.move(0, depth/2, 0, base)
    return base


if __name__ == "__main__":
    #quick test when run directly (requires Maya)
    try:
        t = create_trunk()
        leaves = create_leaves()
        print('oak trunk:', t)
        print('oak leaves count:', len(leaves))
    except Exception as e:
        print('oak_tree_geometry test could not run (Maya may be unavailable):', e)