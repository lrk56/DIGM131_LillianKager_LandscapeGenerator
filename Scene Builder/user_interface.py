'''
User interface for the Landscape Generator inside Maya.
Provides simple controls for terrain, oak and pine parameters and a "Load Scene" button
that assembles a data-driven config and calls `main.build_scene(config_list)`.
'''

try:
	from maya import cmds
except Exception:
	cmds = None

# Do not import main at module import time; import it lazily inside the Load Scene callback
build_scene = None


WINDOW_NAME = 'LandscapeGeneratorUI'


def _float_field(parent, label, minv, maxv, default):
	g = cmds.rowColumnLayout(numberOfColumns=2, parent=parent)
	cmds.text(label=label)
	field = cmds.floatSliderGrp(field=True, minValue=minv, maxValue=maxv, value=default)
	cmds.setParent('..')
	return field


def _int_field(parent, label, minv, maxv, default):
	g = cmds.rowColumnLayout(numberOfColumns=2, parent=parent)
	cmds.text(label=label)
	field = cmds.intSliderGrp(field=True, minValue=minv, maxValue=maxv, value=default)
	cmds.setParent('..')
	return field


def show_ui(on_submit=None):
	if cmds is None:
		print('Maya cmds not available; UI requires Maya to run')
		return

	if cmds.window(WINDOW_NAME, exists=True):
		cmds.deleteUI(WINDOW_NAME)

	window = cmds.window(WINDOW_NAME, title='Landscape Generator', widthHeight=(420, 360))
	tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

	# Terrain tab
	terrain_col = cmds.columnLayout(adj=True)
	t_plane_size = _float_field(terrain_col, 'Plane Size', 1, 200, 40)
	t_subdivs = _int_field(terrain_col, 'Subdivs', 2, 200, 60)
	t_height_scale = _float_field(terrain_col, 'Height Scale', 0.0, 50.0, 4.0)
	t_noise_scale = _float_field(terrain_col, 'Noise Scale', 0.01, 1.0, 0.1)
	cmds.setParent('..')

	# Oak tab
	oak_col = cmds.columnLayout(adj=True)
	o_width = _float_field(oak_col, 'Trunk Width', 0.1, 5.0, 1.0)
	o_height = _float_field(oak_col, 'Trunk Height', 0.5, 20.0, 5.0)
	o_density = _int_field(oak_col, 'Leaf Density', 1, 200, 20)
	o_spread = _float_field(oak_col, 'Leaf Spread', 0.1, 10.0, 2.5)
	cmds.setParent('..')

	# Pine tab
	pine_col = cmds.columnLayout(adj=True)
	p_width = _float_field(pine_col, 'Trunk Width', 0.1, 2.0, 0.4)
	p_height = _float_field(pine_col, 'Trunk Height', 0.5, 30.0, 7.0)
	p_tiers = _int_field(pine_col, 'Tiers', 1, 12, 5)
	p_base_radius = _float_field(pine_col, 'Base Radius', 0.1, 6.0, 2.5)
	cmds.setParent('..')

	cmds.tabLayout(tabs, edit=True, tabLabel=((terrain_col, 'Terrain'), (oak_col, 'Oak'), (pine_col, 'Pine')))

	# Load Scene button
	def _on_load_scene(*args):
		# If an on_submit callback was provided by the caller, prefer that.
		if callable(on_submit):
			try:
				on_submit_cfg = True
			except Exception:
				on_submit_cfg = False
		else:
			on_submit_cfg = False

		cfg = []
		# terrain
		cfg.append({
			'type': 'terrain',
			'plane_size': cmds.floatSliderGrp(t_plane_size, q=True, value=True),
			'subdivs': cmds.intSliderGrp(t_subdivs, q=True, value=True),
			'height_scale': cmds.floatSliderGrp(t_height_scale, q=True, value=True),
			'noise_scale': cmds.floatSliderGrp(t_noise_scale, q=True, value=True),
			'seed': 42,
			'name': 'scene_terrain'
		})

		# single oak
		cfg.append({
			'type': 'oak',
			'width': cmds.floatSliderGrp(o_width, q=True, value=True),
			'height': cmds.floatSliderGrp(o_height, q=True, value=True),
			'density': cmds.intSliderGrp(o_density, q=True, value=True),
			'spread': cmds.floatSliderGrp(o_spread, q=True, value=True),
		})

		# single pine
		cfg.append({
			'type': 'pine',
			'width': cmds.floatSliderGrp(p_width, q=True, value=True),
			'height': cmds.floatSliderGrp(p_height, q=True, value=True),
			'tiers': cmds.intSliderGrp(p_tiers, q=True, value=True),
			'base_radius': cmds.floatSliderGrp(p_base_radius, q=True, value=True),
		})

		# call builder via callback if provided
		if callable(on_submit):
			try:
				results = on_submit(cfg)
				print('on_submit results:', results)
			except Exception:
				import traceback
				traceback.print_exc()
		else:
			# fallback: attempt to import main dynamically and call build_scene
			import sys, os, traceback
			repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
			if repo_root not in sys.path:
				sys.path.insert(0, repo_root)
			try:
				import main
				build_scene_local = getattr(main, 'build_scene', None)
				if build_scene_local is None:
					cmds.confirmDialog(title='Error', message='main.build_scene not found')
					return
				results = build_scene_local(cfg)
				print('build_scene results:', results)
			except Exception:
				msg = 'Failed to import main — see Script Editor for details.'
				cmds.confirmDialog(title='Import Error', message=msg)
				print('Error importing main:')
				traceback.print_exc()

	cmds.columnLayout(adj=True)
	cmds.button(label='Load Scene', height=40, command=_on_load_scene)
	cmds.setParent('..')

	cmds.showWindow(window)


if __name__ == '__main__':
	show_ui()
