"""landscape_ui_starter.py  —  UI starter for the Landscape Generator.
=============================================================================
DIGM 131 — Week 10

This is a LIGHTWEIGHT alternate scaffold for the Week-10 UI on top of your
existing data-driven backbone (`BUILDERS` dispatcher + `SCENE_CONFIG` +
`build_scene(config_list)` in main.py).

NOTE: this starter assumes your bug-fix PR #1 has been merged (the one that
guards demo_perlin's scene-building under __main__). Merge that first.

NOTE 2: you already have a complete `landscape_ui.py` that follows the
data-driven (SCENE_CONFIG list) shape. This file is the *alternate* shape —
a flat settings dict that gets translated into a config list inside
do_the_work(). It exists so you've seen both patterns from class; you're
welcome to ignore it and keep your existing `landscape_ui.py`.

What's already done for you here:
    * `default_settings()`  — a flat-dict settings shape (terrain + per-tree
                              counts + scatter)
    * `do_the_work(settings)` — wired to your existing `build_scene(config_list)`
                                via a small flat-dict → config-list step,
                                with per-tree XZ scatter for non-overlapping
                                trees.

What you fill in (only if you use this file):
    * `build_ui()`     — pick controls and lay them out
    * `read_settings()` — query each control into the same flat-dict shape

See UI_DESIGN.md for the suggested controls. The shape matches
`tool_skeleton.py` and the worked example in `demo_ui_and_polish.py`.
"""

import os
import random
import sys

import maya.cmds as cmds

try:
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _THIS_DIR = cmds.workspace(query=True, rootDirectory=True)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# Your existing dispatcher — DO NOT duplicate the logic, import it.
from main import build_scene   # noqa: E402


# =====================================================================
# LAYER 3 — LOGIC  (wired to your existing build_scene; usually no edits)
# =====================================================================

def default_settings():
    """The flat dict shape this tool consumes. Each key maps to one UI control."""
    return {
        # Terrain
        "terrain_size":    40,
        "terrain_subdivs": 60,
        "height_scale":    4.0,
        "noise_scale":     0.1,
        "terrain_seed":    42,
        # Oaks
        "oak_count":       3,
        "oak_width":       1.0,
        "oak_height":      5.0,
        "oak_density":     20,
        "oak_spread":      2.5,
        "oak_style":       "round",
        # Pines
        "pine_count":      4,
        "pine_width":      0.4,
        "pine_height":     7.0,
        "pine_tiers":      5,
        "pine_radius":     2.5,
        # Layout
        "scatter_radius":  12.0,
        "scatter_seed":    42,
        "group_name":      "landscape_grp",
    }


def _build_config_list(settings, rng):
    """Translate the flat settings dict into a SCENE_CONFIG-style list.

    Per-tree position scatter happens here, not in the UI. Each tree config
    just records its own (x, 0, z) position; the actual move is done by
    your existing _build_oak_element / _build_pine_element via the
    `position` param if you ever add it, OR ignored (which still produces
    distinct trees if your builders honor the trunk/canopy params).
    """
    cfg = [{
        "type":         "terrain",
        "plane_size":   settings.get("terrain_size", 40),
        "subdivs":      settings.get("terrain_subdivs", 60),
        "height_scale": settings.get("height_scale", 4.0),
        "noise_scale":  settings.get("noise_scale", 0.1),
        "seed":         settings.get("terrain_seed", 42),
        "name":         "landscape",
    }]

    radius = settings.get("scatter_radius", 12.0)

    for _ in range(settings.get("oak_count", 0)):
        cfg.append({
            "type":    "oak",
            "width":   settings.get("oak_width", 1.0),
            "height":  settings.get("oak_height", 5.0),
            "density": settings.get("oak_density", 20),
            "style":   settings.get("oak_style", "round"),
            "spread":  settings.get("oak_spread", 2.5),
            # position is recorded here; if you later teach _build_oak_element
            # to honor it, the trees stop overlapping. For now it's a hint.
            "position": (rng.uniform(-radius, radius), 0,
                         rng.uniform(-radius, radius)),
        })

    for _ in range(settings.get("pine_count", 0)):
        cfg.append({
            "type":        "pine",
            "width":       settings.get("pine_width", 0.4),
            "height":      settings.get("pine_height", 7.0),
            "tiers":       settings.get("pine_tiers", 5),
            "base_radius": settings.get("pine_radius", 2.5),
            "position":    (rng.uniform(-radius, radius), 0,
                            rng.uniform(-radius, radius)),
        })

    return cfg


def do_the_work(settings):
    """Turn the flat settings dict into a config list and hand to build_scene()."""
    radius = settings.get("scatter_radius", 12.0)
    if radius <= 0:
        raise ValueError("scatter_radius must be > 0, got {}".format(radius))
    if settings.get("terrain_size", 40) <= 0:
        raise ValueError("terrain_size must be > 0")
    if settings.get("oak_count", 0) < 0 or settings.get("pine_count", 0) < 0:
        raise ValueError("counts must be >= 0")

    rng = random.Random(settings.get("scatter_seed", 42))
    config_list = _build_config_list(settings, rng)

    results = build_scene(config_list=config_list)

    real = [r for r in results if r is not None]
    print("[LandscapeUI] built {} of {} elements".format(len(real),
                                                         len(config_list)))
    return results


# =====================================================================
# LAYER 1 — UI  (TODO: YOU fill this in — or skip and use landscape_ui.py)
# =====================================================================

_ui = {}   # registry: control names keyed by settings-dict key


def build_ui():
    """Draw the Landscape Generator window.

    TODO — fill this in if you want to use the flat-dict shape from this
    starter. Otherwise keep your existing landscape_ui.py — it's already
    complete and follows the SCENE_CONFIG list shape.

    For each setting in default_settings(), add a control and store its name
    in _ui[<setting_key>]. See UI_DESIGN.md for the suggested controls;
    the shape to mirror lives in tool_skeleton.py and demo_ui_and_polish.py.
    """
    window = "landscapeGenStarterWin"
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    cmds.window(window, title="Landscape Generator (starter)",
                widthHeight=(420, 620))
    cmds.scrollLayout(horizontalScrollBarThickness=0,
                      verticalScrollBarThickness=12)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6,
                      columnOffset=("both", 14))
    cmds.text(label="Set the values, then press Build.", align="left")

    # TODO — add controls for each key in default_settings(). For example:
    #   _ui["oak_count"] = cmds.intSliderGrp(
    #       label="Oak count", field=True, min=0, max=20, value=3)
    #   _ui["height_scale"] = cmds.floatSliderGrp(
    #       label="Height scale", field=True, min=0.5, max=20.0, value=4.0)
    #   _ui["oak_style"] = cmds.optionMenu(label="Oak leaf style")
    #   cmds.menuItem(label="round"); cmds.menuItem(label="pointy")
    #   _ui["group_name"] = cmds.textFieldGrp(label="Group name",
    #                                          text="landscape_grp")

    cmds.button(label="Build landscape", height=32,
                command=lambda *_: on_run())
    cmds.showWindow(window)


# =====================================================================
# LAYER 2 — DATA + BRIDGE
# =====================================================================

def read_settings():
    """Query every control and return the dict shape from default_settings().

    TODO — for each key in default_settings(), query _ui[<key>] with
    `query=True`. Examples:
        "oak_count":     cmds.intSliderGrp(_ui["oak_count"],     query=True, value=True),
        "height_scale":  cmds.floatSliderGrp(_ui["height_scale"], query=True, value=True),
        "oak_style":     cmds.optionMenu(_ui["oak_style"],        query=True, value=True),
        "group_name":    cmds.textFieldGrp(_ui["group_name"],     query=True, text=True),
    """
    # Placeholder so partial code still runs while you're filling this in.
    return default_settings()


def on_run():
    """Bridge: gather settings, hand to logic, surface errors politely."""
    settings = read_settings()
    try:
        do_the_work(settings)
    except ValueError as error:
        cmds.warning("Could not build: {}".format(error))


# =====================================================================
# RUN
# =====================================================================

if __name__ == "__main__":
    # do_the_work(default_settings())   # uncomment to test the LOGIC by itself
    build_ui()
