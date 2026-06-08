# UI Design — Landscape Generator

A Week-10 design memo for your Perlin-displaced landscape + oak/pine
generator. This is a **suggestion**, not a constraint. Use it as a starting
point; deviate freely as long as you keep the three-layer separation.

## Heads up: merge your bug-fix PR #1 first

This starter assumes your code **after PR #1 lands** (the one that guards
`demo_perlin.py`'s scene-building under `if __name__ == "__main__":` so
importing `terrain_generator` no longer spawns a stray `terrain` mesh as a
side effect). Merge that first; this UI scaffold builds on top of it.

## You're already ahead of where the assignment expects you to be

Before getting into suggestions, credit where it's due — your most recent
commits already do most of the Week-10 work:

- `main.py::BUILDERS = {"terrain": ..., "oak": ..., "pine": ...}` — a clean
  dispatcher map.
- `main.py::SCENE_CONFIG` + `create_element(data)` + `build_scene(config_list)`
  — the data-driven backbone the lesson is built around.
- `landscape_ui.py` — a full Maya window with terrain / oak / pine
  sections, sliders + dropdowns, a `read_settings()` that returns a
  `SCENE_CONFIG`-shaped list, and an `on_build_clicked()` bridge that calls
  `build_scene(config)`.

So this PR isn't asking you to start over — the design doc below is the
matching write-up for the architecture you've already shipped, and the
starter file is a smaller alternate scaffold (flat settings dict instead of
a `SCENE_CONFIG` list) so you've seen both shapes. Use whichever is more
helpful for the rubric — your existing `landscape_ui.py` already passes
the must-haves.

## Where your project stands today

You already have the data-driven backbone the lesson is built around:

- `main.py::BUILDERS` — the dispatcher (`terrain`, `oak`, `pine`).
- `main.py::SCENE_CONFIG` — a hardcoded list of typed entries.
- `main.py::create_element(data)` — looks up the builder by `type` and
  hands the remaining params via `**params`.
- `main.py::build_scene(config_list)` — drives the dispatcher over a list.
- `main.py::build_landscape()` — older, hardcoded one-of-each demo.
- `landscape_ui.py` — a Maya window producing a `config_list`.

What's left for Week 10 in terms of pedagogy is just *naming* the layers so
the rubric is easy for the TA to check. Everything below is about that.

## The shape you're building toward (recap)

```
UI  →  DATA  →  LOGIC
```

See `demo_ui_and_polish.py` (sections 1, 4, 5) and the `scene_builder/`
package on Notion for the pattern. Your `landscape_ui.py` already follows
it; this doc is the matching write-up. Copy `tool_skeleton.py` if you
ever want to rebuild the window from scratch, or use
`landscape_ui_starter.py` (in this PR) for a flat-dict alternate shape.

## Two valid settings shapes — both are graded equally

Your current `landscape_ui.py::read_settings()` returns a **list of dicts**
(one per element):

```python
[
    {"type": "terrain", "plane_size": 40, ...},
    {"type": "oak", "width": 1.0, "height": 5, ...},
    {"type": "oak", "width": 1.0, "height": 5, ...},   # one entry per tree
    {"type": "pine", ...},
    ...
]
```

That matches `build_scene(config_list)` exactly and is the "data-driven
backbone" shape from class. **Keep this** — it's the more flexible shape
once you start mixing per-element parameters.

The alternate (flat dict) shape the starter file ships with looks like:

```python
{
    "terrain_size":   40,
    "terrain_subdivs":60,
    "height_scale":   4.0,
    "noise_scale":    0.1,
    "terrain_seed":   42,
    "oak_count":      3,
    "oak_width":      1.0,
    "oak_height":     5.0,
    "oak_density":    20,
    "oak_spread":     2.5,
    "oak_style":      "round",
    "pine_count":     4,
    "pine_width":     0.4,
    "pine_height":    7.0,
    "pine_tiers":     5,
    "pine_radius":    2.5,
    "scatter_radius": 12.0,
    "scatter_seed":   42,
    "group_name":     "landscape_grp",
}
```

The starter's `do_the_work(settings)` translates this flat dict back into a
`SCENE_CONFIG`-list and hands it to your existing `build_scene()`. So
either shape ultimately funnels through your dispatcher — nice.

## Suggested UI layout (already broadly matches what you shipped)

| Setting              | Control                              | Range / options    |
|----------------------|--------------------------------------|--------------------|
| `terrain_size`       | `cmds.intSliderGrp`                  | 10 – 200           |
| `terrain_subdivs`    | `cmds.intSliderGrp`                  | 10 – 150           |
| `height_scale`       | `cmds.floatSliderGrp`                | 0.5 – 20.0         |
| `noise_scale`        | `cmds.floatSliderGrp`                | 0.01 – 1.0         |
| `terrain_seed`       | `cmds.intFieldGrp` or slider         | any                |
| `oak_count`          | `cmds.intSliderGrp`                  | 0 – 20             |
| `oak_width`          | `cmds.floatSliderGrp`                | 0.2 – 4.0          |
| `oak_height`         | `cmds.floatSliderGrp`                | 1.0 – 15.0         |
| `oak_density`        | `cmds.intSliderGrp`                  | 5 – 60             |
| `oak_spread`         | `cmds.floatSliderGrp`                | 0.5 – 8.0          |
| `oak_style`          | `cmds.optionMenu`                    | round / pointy     |
| `pine_count`         | `cmds.intSliderGrp`                  | 0 – 20             |
| `pine_width`         | `cmds.floatSliderGrp`                | 0.1 – 2.0          |
| `pine_height`        | `cmds.floatSliderGrp`                | 2.0 – 20.0         |
| `pine_tiers`         | `cmds.intSliderGrp`                  | 2 – 10             |
| `pine_radius`        | `cmds.floatSliderGrp`                | 0.5 – 8.0          |
| `scatter_radius`     | `cmds.floatSliderGrp`                | 2.0 – 30.0         |
| `scatter_seed`       | `cmds.intFieldGrp`                   | any                |
| `group_name`         | `cmds.textFieldGrp`                  | any valid name     |
|                      | `cmds.button("Build landscape")`     | calls `on_run()`   |

Window size around `420 × 620` matches what you already shipped. A
`scrollLayout` wrapping the `columnLayout` (also already in your code) is
the right call for this many controls.

## How the layers map to your existing code

- **LOGIC — `do_the_work(settings)` (or your `build_scene(config_list)`)**:
  consumes the settings, produces a `SCENE_CONFIG`-style list, and calls
  `build_scene(config_list)`. Scatter the per-tree positions with
  `random.Random(settings["scatter_seed"])` if you want deterministic
  layouts; your current UI builds N identical-position dicts, which is also
  fine for now.

- **DATA — `read_settings()`**: query each control with `query=True` and
  return either the flat dict or the `SCENE_CONFIG` list. Your existing
  `landscape_ui.read_settings()` already does the list shape — perfect.

- **UI — `build_ui()`**: window → `scrollLayout` → `columnLayout` →
  controls → button → show. No logic in here, not even reading the
  controls — that lives in `read_settings()`. Your `landscape_ui.build_ui()`
  already follows this rule.

- **BRIDGE — `on_run()` (your `on_build_clicked`)**: 4 lines. Gather
  settings, call into logic, surface `ValueError` via `cmds.warning(...)`.

## Must-have vs. nice-to-have

**Must-have** (for the grading rubric):
- All three layers separated; no scene-building code inside the callback.
  *(You're already here.)*
- At least 4 working controls. *(You have ~17.)*
- A "Build" button that calls into your dispatcher via a settings shape.
  *(Done.)*
- A `default_settings()` / `read_settings()` shape that matches what
  `build_ui()` produces. *(Your `read_settings()` does this; consider
  adding an explicit `default_settings()` for parity with the demo.)*
- Friendly error path: `cmds.warning(...)` on `ValueError`, no raw traceback
  in the Script Editor for normal bad input. *(You re-raise after warning;
  swallowing for `ValueError` would be more rubric-friendly.)*

**Nice-to-have** (extra polish):
- Per-tree position scatter using `random.Random(seed)` so you can keep
  `oak_count` and `pine_count` without overlapping trees. *(The starter
  file shows this in `do_the_work`.)*
- "Clear scene" button next to "Build" (`cmds.file(new=True, force=True)`).
  *(Your "Reset Defaults" button is similar but keeps the scene.)*
- Persist a settings dict to JSON via `cmds.fileDialog2` so artists can
  save/restore presets.
- A shelf-button installer following Section 8 of the demo.
- Add a `rocks` builder type to `BUILDERS` (you've experimented with
  `rock_geometry.py` before — easy lift now that the dispatcher exists).

## How to use the starter file in this PR

`landscape_ui_starter.py` is the lightweight alternate scaffold:

- `default_settings()` and `do_the_work()` are **written** and already wire
  to your `build_scene()` via a flat-dict → config-list translation, with
  per-tree XZ scatter. You shouldn't need to change them.
- `build_ui()` and `read_settings()` are **stubbed** with TODO comments in
  the right shape — only if you want to practice the flat-dict pattern.

You can ignore the starter entirely and keep your existing `landscape_ui.py`
— **that's the recommended path**. The starter exists so you've seen the
other common shape from class and the matching design doc.

## Resources

- **`tool_skeleton.py`** — the blank version of this pattern.
- **`demo_ui_and_polish.py`** — read sections 1, 4, 5 first; section 8 for
  the shelf-button finish.
- **`scene_builder/` package** — the recommended multi-file layout if you
  want to split UI and logic across files.

Questions? Comment on this PR or message me.
