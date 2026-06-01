"""tree_materials.py
Utility module for creating and assigning materials to tree geometry in Autodesk Maya.
Contains functions for shader creation and material assignment.
"""
from maya import cmds


def create_material(color=(0.4, 0.25, 0.1), texture_path=None):
    """
    Creates a Lambert shader with an optional file texture.

    Args:
        color (tuple): RGB color values between 0 and 1. Defaults to a brown bark color (0.4, 0.25, 0.1).
        texture_path (str): Absolute path to a texture file. If None, uses flat color. Defaults to None.

    Returns:
        str: Name of the created shader node.
    """
    shader = cmds.shadingNode('lambert', asShader=True)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader + 'SG')
    cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)

    if texture_path:
        #create a file texture node and connect it to the shader color
        file_node = cmds.shadingNode('file', asTexture=True)
        cmds.setAttr(file_node + '.fileTextureName', texture_path, type='string')
        cmds.connectAttr(file_node + '.outColor', shader + '.color', force=True)
    else:
        #apply flat color if no texture path provided
        cmds.setAttr(shader + '.color', color[0], color[1], color[2], type='double3')

    return shader


def assign_material(obj, material):
    """
    Assigns an existing shader to a Maya object or list of objects.

    Args:
        obj (str or list): Name of the Maya transform node or a list of node names to assign the material to.
        material (str): Name of the shader node to assign.

    Returns:
        str: Name of the shading group the material was assigned through.
    """
    #find the shading group connected to this shader
    shading_groups = cmds.listConnections(material + '.outColor', type='shadingEngine')

    if not shading_groups:
        raise RuntimeError(f"No shading group found for material: {material}")

    shading_group = shading_groups[0]

    #handle both single objects and lists
    if isinstance(obj, list):
        for o in obj:
            cmds.sets(o, edit=True, forceElement=shading_group)
    else:
        cmds.sets(obj, edit=True, forceElement=shading_group)

    return shading_group


if __name__ == "__main__":
    try:
        mat = create_material((0.13, 0.45, 0.1))
        print('tree material created:', mat)
    except Exception as e:
        print('tree_materials test could not run:', e)