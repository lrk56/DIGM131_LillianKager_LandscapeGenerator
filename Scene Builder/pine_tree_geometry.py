"""pine_tree_geometry.py
Utility module for generating a stylized pine tree in Autodesk Maya.
Pine trees use a tapered trunk and stacked cone layers for foliage instead of round canopy clusters.
"""
from maya import cmds
import math

#DEBUG flag - when True builder functions will print parameters and errors
DEBUG = False


def create_trunk(width=0.4, height=7):
    """
    Creates a tapered cylindrical trunk narrow at the top, wider at the base.

    Args:
        width (float): Radius of the trunk base. Defaults to 0.4.
        height (float): Height of the trunk. Defaults to 7.

    Returns:
        str: Name of the created trunk transform node.
    """
    if width <= 0:
        if DEBUG: print('create_trunk (pine): invalid width, using default 0.4')
        width = 0.4
    if height <= 0:
        if DEBUG: print('create_trunk (pine): invalid height, using default 7')
        height = 7
    try:
        trunk = cmds.polyCylinder(h=height, r=width/2, sx=8, sy=1, sz=1)[0]
        #taper the top of the trunk to be narrower so it feels natural
        cmds.select(trunk + '.vtx[8]')
        cmds.scale(0.3, 1, 0.3, relative=True)
        cmds.move(0, height/2, 0, trunk)
        return trunk
    except Exception as e:
        if DEBUG: print('pine create_trunk failed:', e)
        return None



def create_foliage(tiers=5, base_radius=2.5, trunk_height=7):
    """
    Creates stacked cone layers that form the classic pine tree silhouette.

    Args:
        tiers (int): Number of foliage cone layers stacked vertically. Defaults to 5.
        base_radius (float): Radius of the widest bottom cone. Defaults to 2.5.
        trunk_height (float): Height of the trunk so cones are placed correctly. Defaults to 7.

    Returns:
        list[str]: List of foliage cone transform node names.
    """
    cones = []
    if tiers <= 0:
        if DEBUG:
            print('create_foliage: invalid tiers, using default 5')
        tiers = 5
    try:
        for i in range(tiers):
            #each tier gets smaller and higher up
            t = i / tiers
            radius = base_radius * (1.0 - t * 0.7)
            cone_height = radius * 1.6
            #tiers start at bottom third of trunk and stack to the tip
            y = trunk_height * 0.25 + (trunk_height * 0.75 * t)

            cone = cmds.polyCone(h=cone_height, r=radius, sx=8, sy=1)[0]
            #place cone at the right height for this tier
            cmds.move(0, y, 0, cone)
            cones.append(cone)
        return cones
    except Exception as e:
        if DEBUG:
            print('create_foliage failed:', e)
        return []


def create_base(depth=1.0, radius=0.8):
    """
    Creates a small flared cone at the base of the trunk to ground the tree.

    Args:
        depth (float): Height of the base cone. Defaults to 1.0.
        radius (float): Radius of the base flare. Defaults to 0.8.

    Returns:
        str: Name of the created base transform node.
    """
    try:
        base = cmds.polyCone(h=depth, r=radius, sx=8, sy=1)[0]
        #little flare to make the base look grounded
        cmds.move(0, depth/2, 0, base)
        return base
    except Exception as e:
        if DEBUG: print('pine create_base failed:', e)
        return None


if __name__ == "__main__":
    try:
        t = create_trunk()
        foliage = create_foliage()
        print('pine trunk:', t)
        print('pine foliage tiers:', len(foliage))
    except Exception as e:
        print('pine_tree_geometry test could not run:', e)