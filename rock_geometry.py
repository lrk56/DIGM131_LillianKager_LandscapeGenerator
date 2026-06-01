"""rock_geometry.py
Utility module for generating rocks in Autodesk Maya.
Contains builder function for rock
"""
from maya import cmds
import random

def create_rock(radius=None, position=(0, 0, 0):
  """Create a rock that uses randommized radius sizes

  Args:
    radius (float):    radius of the rock
    position (tuple):  (x, y, z) coordinates of the rock
  """
  #creates the rock
  rock = cmds.polysphere(radius=radius, name="rock_#")[0]

  if radius == None:
    radius = random.uniform(2,5)

  return rock


