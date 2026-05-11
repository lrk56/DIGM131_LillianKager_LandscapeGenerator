"""terrain_materials.py
Utility module for creating and assigning materials to terrain geometry in Autodesk Maya.
Includes presets for grass, sand, and stone with fully customizable color overrides.
"""
from maya import cmds


#preset color palettes — edit these to quickly change the look of each terrain type
PRESETS = {
    'grass': {
        'color':     (0.15, 0.4,  0.1),
        'ambience':  (0.05, 0.15, 0.04),
        'diffuse':   0.9,
    },
    'sand': {
        'color':     (0.76, 0.65, 0.4),
        'ambience':  (0.3,  0.25, 0.15),
        'diffuse':   0.8,
    },
    'stone': {
        'color':     (0.45, 0.45, 0.45),
        'ambience':  (0.15, 0.15, 0.15),
        'diffuse':   0.7,
    },
}


def create_terrain_material(preset='grass', color=None, ambience=None, diffuse=None):
    """
    Creates a Lambert shader for terrain using a named preset with optional color overrides.
    Any parameter passed in will override the preset value, making it easy to tweak.

    Args:
        preset (str): Base style to use — 'grass', 'sand', or 'stone'. Defaults to 'grass'.
        color (tuple): RGB override for the main surface color. e.g. (0.2, 0.5, 0.1). Defaults to None.
        ambience (tuple): RGB override for the ambient light color. Defaults to None.
        diffuse (float): Override for diffuse intensity between 0 and 1. Defaults to None.

    Returns:
        str: Name of the created shader node.
    """
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset '{preset}'. Choose from: {list(PRESETS.keys())}")

    #start from preset then apply any overrides on top
    settings = PRESETS[preset].copy()
    if color    is not None: settings['color']    = color
    if ambience is not None: settings['ambience'] = ambience
    if diffuse  is not None: settings['diffuse']  = diffuse

    shader = cmds.shadingNode('lambert', asShader=True, name=f'terrain_{preset}_mat')
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader + 'SG')
    cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)

    #apply settings to shader nodes
    cmds.setAttr(shader + '.color',     *settings['color'],    type='double3')
    cmds.setAttr(shader + '.ambientColor', *settings['ambience'], type='double3')
    cmds.setAttr(shader + '.diffuse',   settings['diffuse'])

    return shader


def assign_terrain_material(terrain, material):
    """
    Assigns a shader to a terrain mesh object.

    Args:
        terrain (str): Name of the Maya terrain transform node.
        material (str): Name of the shader node to assign.

    Returns:
        str: Name of the shading group the material was assigned through.
    """
    shading_groups = cmds.listConnections(material + '.outColor', type='shadingEngine')

    if not shading_groups:
        raise RuntimeError(f"No shading group found for material: {material}")

    shading_group = shading_groups[0]
    #apply material to the terrain object
    cmds.sets(terrain, edit=True, forceElement=shading_group)
    return shading_group