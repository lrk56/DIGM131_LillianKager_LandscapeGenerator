"""landscape_ui.py
Maya UI window for DIGM131 LandscapeGenerator — Week 9/10
Follows the UI -> DATA -> LOGIC pattern from class:
  - build_ui()             draws the window (no scene logic)
  - read_settings()        turns controls into a SCENE_CONFIG list (data layer)
  - on_build_clicked()     bridge: read settings -> hand to build_scene()
  - build_scene()          logic in main.py (unchanged)

HOW TO RUN (inside Maya Script Editor):
    import landscape_ui
    landscape_ui.build_ui()

Or after first run:
    import importlib, landscape_ui
    importlib.reload(landscape_ui)
    landscape_ui.build_ui()
"""

import maya.cmds as cmds

#import the logic layer (same files you already have)
import sys, os
_DIR = os.path.dirname(__file__)
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from main import build_scene   #build_scene(config_list) in your main.py

#WINDOW / CONTROL NAMES  (module-level constants so every function agrees)
_WIN = "landscapeGeneratorWin"

#Terrain
_T_SIZE      = "lg_terrain_size"
_T_SUBDIVS   = "lg_terrain_subdivs"
_T_HEIGHT    = "lg_terrain_height"
_T_NOISE     = "lg_terrain_noise"
_T_SEED      = "lg_terrain_seed"
_T_PRESET    = "lg_terrain_preset"   #optionMenu for material preset

#Oak tree section
_OAK_COUNT   = "lg_oak_count"
_OAK_WIDTH   = "lg_oak_width"
_OAK_HEIGHT  = "lg_oak_height"
_OAK_DENSITY = "lg_oak_density"
_OAK_SPREAD  = "lg_oak_spread"
_OAK_STYLE   = "lg_oak_style"        #optionMenu: round / pointy

#Pine tree section
_PINE_COUNT  = "lg_pine_count"
_PINE_WIDTH  = "lg_pine_width"
_PINE_HEIGHT = "lg_pine_height"
_PINE_TIERS  = "lg_pine_tiers"
_PINE_RADIUS = "lg_pine_radius"

#HELPER WIDGETS  (keep build_ui() readable)

def _section_label(text):
    """Bold-ish separator label for a control group."""
    cmds.separator(h=6, style="in")
    cmds.text(label="  " + text, align="left", font="boldLabelFont", h=20)
    cmds.separator(h=4, style="none")


def _int_row(label, ctl_name, value, lo, hi):
    """One labeled integer slider+field row."""
    cmds.intSliderGrp(
        ctl_name,
        label=label, field=True,
        min=lo, max=hi, value=value,
        columnWidth=[(1, 130), (2, 50), (3, 120)],
        columnAlign=[(1, "right")],
    )


def _float_row(label, ctl_name, value, lo, hi, step=0.1):
    """One labeled float slider+field row."""
    cmds.floatSliderGrp(
        ctl_name,
        label=label, field=True,
        min=lo, max=hi, value=value, step=step,
        columnWidth=[(1, 130), (2, 60), (3, 110)],
        columnAlign=[(1, "right")],
    )

# DATA LAYER — read the UI into a SCENE_CONFIG list

def read_settings():
    """Query every control and return a SCENE_CONFIG list ready for build_scene().

    This is the ONLY place that knows both 'what controls exist' and
    'what shape build_scene() expects'. Neither the UI nor the logic
    touches this directly — it is the data layer bridge.

    Returns:
        list[dict]: A SCENE_CONFIG list matching the format in main.py.
    """
    #terrain
    terrain_preset = cmds.optionMenu(_T_PRESET, q=True, v=True)   #'grass'|'sand'|'stone'

    config = [
        {
            "type":         "terrain",
            "plane_size":   cmds.intSliderGrp(_T_SIZE,    q=True, v=True),
            "subdivs":      cmds.intSliderGrp(_T_SUBDIVS, q=True, v=True),
            "height_scale": cmds.floatSliderGrp(_T_HEIGHT, q=True, v=True),
            "noise_scale":  cmds.floatSliderGrp(_T_NOISE,  q=True, v=True),
            "seed":         cmds.intSliderGrp(_T_SEED,    q=True, v=True),
            "name":         "landscape",
            #terrain_preset is forwarded so main.py / terrain_materials can use it
            #(main.py's _build_terrain_element passes **params to create_terrain,
            #which doesn't take 'preset' — so we store it separately below)
        }
    ]

    #oak trees (one dict per tree instance)
    oak_count   = cmds.intSliderGrp(_OAK_COUNT,   q=True, v=True)
    oak_width   = cmds.floatSliderGrp(_OAK_WIDTH,  q=True, v=True)
    oak_height  = cmds.floatSliderGrp(_OAK_HEIGHT, q=True, v=True)
    oak_density = cmds.intSliderGrp(_OAK_DENSITY,  q=True, v=True)
    oak_spread  = cmds.floatSliderGrp(_OAK_SPREAD,  q=True, v=True)
    oak_style   = cmds.optionMenu(_OAK_STYLE, q=True, v=True)   # 'round'|'pointy'

    for _ in range(oak_count):
        config.append({
            "type":    "oak",
            "width":   oak_width,
            "height":  oak_height,
            "density": oak_density,
            "style":   oak_style,
            "spread":  oak_spread,
        })

    #pine trees
    pine_count  = cmds.intSliderGrp(_PINE_COUNT,  q=True, v=True)
    pine_width  = cmds.floatSliderGrp(_PINE_WIDTH,  q=True, v=True)
    pine_height = cmds.floatSliderGrp(_PINE_HEIGHT, q=True, v=True)
    pine_tiers  = cmds.intSliderGrp(_PINE_TIERS,  q=True, v=True)
    pine_radius = cmds.floatSliderGrp(_PINE_RADIUS, q=True, v=True)

    for _ in range(pine_count):
        config.append({
            "type":        "pine",
            "width":       pine_width,
            "height":      pine_height,
            "tiers":       pine_tiers,
            "base_radius": pine_radius,
        })

    return config

# BRIDGE — callback that sits between the button and the logic

def on_build_clicked(*_args):
    """Button callback. Reads settings, calls build_scene(). No scene logic here."""
    try:
        config = read_settings()
        print("[LandscapeUI] Building scene with {} elements...".format(len(config)))
        results = build_scene(config)
        built = [r for r in results if r is not None]
        print("[LandscapeUI] Done — {} element(s) created successfully.".format(len(built)))
    except Exception as e:
        cmds.warning("Landscape build failed: {}".format(e))
        raise


def on_reset_clicked(*_args):
    """Restore all controls to their original defaults."""
    cmds.intSliderGrp(_T_SIZE,      e=True, v=40)
    cmds.intSliderGrp(_T_SUBDIVS,   e=True, v=60)
    cmds.floatSliderGrp(_T_HEIGHT,  e=True, v=4.0)
    cmds.floatSliderGrp(_T_NOISE,   e=True, v=0.1)
    cmds.intSliderGrp(_T_SEED,      e=True, v=42)
    cmds.optionMenu(_T_PRESET,      e=True, v="grass")

    cmds.intSliderGrp(_OAK_COUNT,   e=True, v=3)
    cmds.floatSliderGrp(_OAK_WIDTH, e=True, v=1.0)
    cmds.floatSliderGrp(_OAK_HEIGHT,e=True, v=5.0)
    cmds.intSliderGrp(_OAK_DENSITY, e=True, v=20)
    cmds.floatSliderGrp(_OAK_SPREAD,e=True, v=2.5)
    cmds.optionMenu(_OAK_STYLE,     e=True, v="round")

    cmds.intSliderGrp(_PINE_COUNT,  e=True, v=4)
    cmds.floatSliderGrp(_PINE_WIDTH,e=True, v=0.4)
    cmds.floatSliderGrp(_PINE_HEIGHT,e=True, v=7.0)
    cmds.intSliderGrp(_PINE_TIERS,  e=True, v=5)
    cmds.floatSliderGrp(_PINE_RADIUS,e=True, v=2.5)
    print("[LandscapeUI] Controls reset to defaults.")

# UI LAYER - draws the window and contains NO scene logic

def build_ui():
    """Open the Landscape Generator window.

    The window only produces a data dict and hands it to the logic.
    No geometry or material code lives here.
    """
    #Always delete the old window first (the classic Maya gotcha)
    if cmds.window(_WIN, exists=True):
        cmds.deleteUI(_WIN)

    cmds.window(
        _WIN,
        title="Landscape Generator",
        widthHeight=(420, 620),
        sizeable=True,
        menuBar=False,
    )

    #Outer scroll layout so the window can be resized small without clipping
    cmds.scrollLayout(horizontalScrollBarThickness=0, verticalScrollBarThickness=12)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4,
                      columnAttach=("both", 10))

    #Title
    cmds.separator(h=8, style="none")
    cmds.text(label="Landscape Generator", align="center",
              font="boldLabelFont", h=26)
    cmds.text(label="DIGM 131  |  Lillian Kager", align="center", h=18)
    cmds.separator(h=6, style="double")

    #TERRAIN
    _section_label("Terrain")
    _int_row(  "Plane size",   _T_SIZE,    40,  10, 200)
    _int_row(  "Subdivisions", _T_SUBDIVS, 60,  10, 150)
    _float_row("Height scale", _T_HEIGHT,  4.0, 0.5, 20.0)
    _float_row("Noise scale",  _T_NOISE,   0.1, 0.01, 1.0, step=0.01)
    _int_row(  "Random seed",  _T_SEED,    42,  0,  999)

    #Material preset dropdown
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(140, 200),
                   columnAlign=[(1, "right")], columnAttach=[(1, "right", 5)])
    cmds.text(label="Material preset")
    cmds.optionMenu(_T_PRESET)
    for p in ("grass", "sand", "stone"):
        cmds.menuItem(label=p)
    cmds.setParent("..")

    #OAK TREES
    _section_label("Oak Trees")
    _int_row(  "Number of oaks", _OAK_COUNT,   3, 0, 20)
    _float_row("Trunk width",    _OAK_WIDTH,   1.0, 0.2, 4.0)
    _float_row("Trunk height",   _OAK_HEIGHT,  5.0, 1.0, 15.0)
    _int_row(  "Leaf density",   _OAK_DENSITY, 20, 5, 60)
    _float_row("Canopy spread",  _OAK_SPREAD,  2.5, 0.5, 8.0)

    #Leaf style dropdown
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(140, 200),
                   columnAlign=[(1, "right")], columnAttach=[(1, "right", 5)])
    cmds.text(label="Leaf style")
    cmds.optionMenu(_OAK_STYLE)
    for s in ("round", "pointy"):
        cmds.menuItem(label=s)
    cmds.setParent("..")

    #PINE TREES
    _section_label("Pine Trees")
    _int_row(  "Number of pines",  _PINE_COUNT,  4, 0, 20)
    _float_row("Trunk width",      _PINE_WIDTH,  0.4, 0.1, 2.0)
    _float_row("Trunk height",     _PINE_HEIGHT, 7.0, 2.0, 20.0)
    _int_row(  "Foliage tiers",    _PINE_TIERS,  5, 2, 10)
    _float_row("Base cone radius", _PINE_RADIUS, 2.5, 0.5, 8.0)

    #BUTTONS
    cmds.separator(h=10, style="in")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 200),
                   columnAttach=[("both", 6)], columnAlign=[(1, "center"), (2, "center")])
    cmds.button(label="Build Scene", h=36,
                backgroundColor=(0.25, 0.55, 0.25),
                command=on_build_clicked)
    cmds.button(label="Reset Defaults", h=36,
                command=on_reset_clicked)
    cmds.setParent("..")

    cmds.separator(h=10, style="none")

    #Done so show the window
    cmds.showWindow(_WIN)
    print("[LandscapeUI] Window opened.")


#Allow running directly from Script Editor
if __name__ == "__main__":
    build_ui()