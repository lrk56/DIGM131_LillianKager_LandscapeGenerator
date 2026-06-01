"""oak_tree_geometry.py
Utility module for generating a stylized oak tree in Autodesk Maya.
Contains builder functions for trunk, branches, foliage, and base geometry.
"""
from maya import cmds
import random
import math


def create_trunk(width=1, height=5):
    """
    Creates a cylindrical trunk mesh centered at the world origin.

    Args:
        width (float): Diameter of the trunk. Defaults to 1.
        height (float): Height of the trunk. Defaults to 5.

    Returns:
        str: Name of the created trunk transform node.
    """
    trunk = cmds.polyCylinder(h=height, r=width/2, sx=8, sy=1, sz=1)[0]
    #move trunk so it sits on the ground
    cmds.move(0, height/2, 0, trunk)
    return trunk

def create_branches(count=5, spread=3, trunk_height=5):
    """
    Generates branch cylinders fanned outward from the top of the trunk.

    Arguments:
        count (int): Number of branches to generate. Defaults to 5.
        spread (float): Length of each branch. Defaults to 3.
        trunk_height (float): Y position of the trunk top to attach branches. Defaults to 5.
    Returns:
        list[str]: List of branch transform node names.
    """
    branches = []
    for i in range(count):
        angle = (360.0 / count) * i
        branch = cmds.polyCylinder(h=spread, r=0.1, sx=8, sy=1, sz=1)[0]
        #rotate around Y first so each branch faces outward at its angle
        cmds.xform(branch, ro=(0, angle, -60), ws=True)

        #place at top of trunk offset outward slightly
        rad = math.radians(angle)
        cmds.move(math.sin(rad) * 0.3, trunk_height, math.cos(rad) * 0.3, branch)

        branches.append(branch)
    return branches

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