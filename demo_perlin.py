import maya.cmds as cmds
import math
import random


#--- Simple value noise (Perlin-like) ---
def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(a, b, t):
    return a + t * (b - a)


#Grid-based gradient noise
class PerlinNoise:
    def __init__(self, seed=0):
        random.seed(seed)
        self.gradients = {}

    def _gradient(self, ix, iy):
        if (ix, iy) not in self.gradients:
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[(ix, iy)] = (math.cos(angle), math.sin(angle))
        return self.gradients[(ix, iy)]

    def _dot_grid(self, ix, iy, x, y):
        gx, gy = self._gradient(ix, iy)
        dx, dy = x - ix, y - iy
        return gx * dx + gy * dy

    def noise(self, x, y):
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        x1, y1 = x0 + 1, y0 + 1
        sx, sy = fade(x - x0), fade(y - y0)
        n00 = self._dot_grid(x0, y0, x, y)
        n10 = self._dot_grid(x1, y0, x, y)
        n01 = self._dot_grid(x0, y1, x, y)
        n11 = self._dot_grid(x1, y1, x, y)
        return lerp(lerp(n00, n10, sx), lerp(n01, n11, sx), sy)

    def fractal(self, x, y, octaves=4, persistence=0.5, lacunarity=2.0):
        total, amp, freq = 0.0, 1.0, 1.0
        for _ in range(octaves):
            total += self.noise(x * freq, y * freq) * amp
            amp *= persistence
            freq *= lacunarity
        return total


if __name__ == "__main__":
    # Settings
    subdivs = 50
    plane_size = 20
    noise_scale = 0.15  # controls feature size (lower = broader hills)
    height_scale = 5.0  # max displacement height

    # Create the plane
    terrain = cmds.polyPlane(
        w=plane_size, h=plane_size,
        sx=subdivs, sy=subdivs,
        name='terrain'
    )[0]
#Settings
subdivs = 50
plane_size = 20
noise_scale = 0.15  # controls feature size (lower = broader hills)
height_scale = 5.0  # max displacement height

#Create the plane
terrain = cmds.polyPlane(
    w=plane_size, h=plane_size,
    sx=subdivs, sy=subdivs,
    name='terrain'
)[0]

    perlin = PerlinNoise(seed=42)

    # Displace each vertex along Y
    num_verts = cmds.polyEvaluate(terrain, vertex=True)
    for i in range(num_verts):
        vtx = '{}.vtx[{}]'.format(terrain, i)
        pos = cmds.pointPosition(vtx, world=True)
        h = perlin.fractal(pos[0] * noise_scale, pos[2] * noise_scale,
                           octaves=4, persistence=0.5)
        cmds.xform(vtx, worldSpace=True, translation=[pos[0], h * height_scale, pos[2]])
#Displace each vertex along Y
num_verts = cmds.polyEvaluate(terrain, vertex=True)
for i in range(num_verts):
    vtx = '{}.vtx[{}]'.format(terrain, i)
    pos = cmds.pointPosition(vtx, world=True)
    h = perlin.fractal(pos[0] * noise_scale, pos[2] * noise_scale,
                       octaves=4, persistence=0.5)
    cmds.xform(vtx, worldSpace=True, translation=[pos[0], h * height_scale, pos[2]])
