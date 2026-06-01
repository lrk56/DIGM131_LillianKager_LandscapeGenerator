"""terrain_generation.py
Utility module for generating Perlin noise-based terrain in Autodesk Maya.
Wraps the demo_perlin module to expose a ymore simple interface for creating custom terrain meshes.
"""

#simple wrapper so other files can call create_terrain() easily
import sys
import os

#add the current directory to sys.path so demo_perlin can be found
sys.path.insert(0, os.path.dirname(__file__))

import maya.cmds as cmds
from demo_perlin import PerlinNoise


def create_terrain(
    plane_size=20,
    subdivs=50,
    height_scale=5.0,
    noise_scale=0.15,
    octaves=4,
    persistence=0.5,
    lacunarity=2.0,
    seed=42,
    name='terrain'
):
    """
    Creates a displaced terrain mesh in the Maya viewport using Perlin fractal noise.

    Args:
        plane_size (float): Width and height of the terrain plane in world units. Defaults to 20.
        subdivs (int): Number of subdivisions along each axis. Higher values give more detail. Defaults to 50.
        height_scale (float): Maximum vertical displacement height. Defaults to 5.0.
        noise_scale (float): Controls feature size of the noise. Lower values produce broader hills. Defaults to 0.15.
        octaves (int): Number of noise layers to stack for fractal detail. Defaults to 4.
        persistence (float): How much each octave contributes relative to the last. Defaults to 0.5.
        lacunarity (float): How much the frequency increases per octave. Defaults to 2.0.
        seed (int): Random seed for reproducible terrain. Defaults to 42.
        name (str): Name of the resulting Maya mesh node. Defaults to 'terrain'.

    Returns:
        str: Name of the created terrain transform node.
    """
    #create the base plane
    terrain = cmds.polyPlane(
        w=plane_size, h=plane_size,
        sx=subdivs, sy=subdivs,
        name=name
    )[0]

    #make perlin instance for displacement
    perlin = PerlinNoise(seed=seed)

    #displace each vertex along Y using fractal noise,one by one
    num_verts = cmds.polyEvaluate(terrain, vertex=True)
    for i in range(num_verts):
        vtx = '{}.vtx[{}]'.format(terrain, i)
        pos = cmds.pointPosition(vtx, world=True)
        h = perlin.fractal(
            pos[0] * noise_scale,
            pos[2] * noise_scale,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity
        )
        #move vertex up by noise value scaled to height_scale
        cmds.xform(vtx, worldSpace=True, translation=[pos[0], h * height_scale, pos[2]])

    return terrain