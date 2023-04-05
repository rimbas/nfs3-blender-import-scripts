from collections import defaultdict
import json
import numpy as np
import dearpygui.dearpygui as dpg
from atlas_uv_mapper import TextureUvEntry

UVDict = dict[int, TextureUvEntry]

with open("TR060-uv_mapping.json", "r", encoding="utf8") as f:
	aquatica: UVDict = {int(k): TextureUvEntry(**j) for k, j in json.load(f).items()}
	aquatica_rows = defaultdict(list)

with open("TR020-uv_mapping.json", "r", encoding="utf8") as f:
	atlantica: UVDict = {int(k): TextureUvEntry(**j) for k, j in json.load(f).items()}
	atlantica_rows = defaultdict(list)

with open("uv_remap_TR020_TR060.json", "r", encoding="utf8") as f:
	remapping = {int(k): v for k, v in json.load(f).items()}

dpg.create_context()
dpg.configure_app(manual_callback_management=True)

tex_w, tex_h, tex_channels, data = dpg.load_image("TR060+020.png")

with dpg.texture_registry():
	dpg.add_static_texture(width=tex_w, height=tex_h, default_value=data, tag="atlas_texture")

COLOR_SOURCE = (13, 152, 186, 255)
COLOR_DEST = (252, 194, 0, 255)

with dpg.window(label="Atlas") as main_window:
	with dpg.drawlist(width=tex_w+100, height=tex_h+100):
		with dpg.draw_node(tag="atlas_drawlist_root") as atlas_drawlist:
			dpg.draw_image("atlas_texture", (0, 0), (tex_w, tex_h))
			atlas_source = [
				dpg.draw_polyline([(0, 0), (20, 0), (20, 20), (0, 20)], closed=True, thickness=3, color=COLOR_SOURCE),
				dpg.draw_circle((0, 0), radius=5, color=COLOR_SOURCE),
			]
			atlas_destination = [
				dpg.draw_polyline([(100, 100), (120, 100), (120, 120), (100, 120)], closed=True, thickness=3, color=COLOR_DEST),
				dpg.draw_circle((100, 100), radius=5, color=COLOR_DEST),
			]
		dpg.apply_transform("atlas_drawlist_root", dpg.create_translation_matrix([30, 30]))

with dpg.window(label="UV Preview"):
	with dpg.drawlist(width = 512+20, height = 256) as uv_preview_drawlist:
		source_uv_drawlist = dpg.draw_image("atlas_texture", (0, 0), (256, 256), uv_min=(0.5, 0.5), uv_max=(0.5+128/1024, 0.5+128/1024))
		destination_uv_drawlist = dpg.draw_image("atlas_texture", (256+20, 0), (512+20, 256), uv_min=(0.5, 0.5), uv_max=(0.5+128/1024, 0.5+128/1024))

def create_uv_listing(uvs: UVDict, dpg_collection: dict[int, list], name, button_callback):
	with dpg.table(header_row=True):
		dpg.add_table_column(label="Button")
		dpg.add_table_column(label="Source ID")
		dpg.add_table_column(label="Source texture")
		dpg.add_table_column(label="Size")

		for key, uv_entry in uvs.items():
			dpg_row = dpg_collection[key]
			with dpg.table_row() as table_row:
				dpg.add_button(label=f"{name}", callback=button_callback, user_data=key)
				dpg_row.append(dpg.add_text(f"{key}"))
				dpg_row.append(dpg.add_text(f"{uv_entry.id}"))
				dpg_row.append(dpg.add_text(f"{uv_entry.texture_size}"))
			

def draw_uv_preview(renderables: list, color, entry: TextureUvEntry):
	uv = [(x * entry.atlas_size, (1-y) * entry.atlas_size) for x, y in entry.corners]
	for r in renderables:
		dpg.delete_item(r)
	renderables.clear()
	renderables.append(dpg.draw_polyline(uv, closed=True, thickness=3, color=color, parent=atlas_drawlist))
	renderables.append(dpg.draw_circle(uv[0], radius=7, thickness=3, color=color, fill=True, parent=atlas_drawlist))
	renderables.append(dpg.draw_circle(uv[0], radius=5, thickness=3, color=(0, 0, 0, 255), fill=True, parent=atlas_drawlist))

source_id = None
destination_id = None

def set_source_uv(sender, app_data, user_data):
	global source_id, atlas_source, source_uv_drawlist
	source_id = user_data
	entry = atlantica[source_id]
	draw_uv_preview(atlas_source, COLOR_SOURCE, entry)
	dpg.delete_item(source_uv_drawlist)
	uv_min = min(x for x, y in entry.corners), min(1-y for x, y in entry.corners)
	uv_max = max(x for x, y in entry.corners), max(1-y for x, y in entry.corners)
	source_uv_drawlist = dpg.draw_image("atlas_texture", (0, 0), (256, 256), uv_min=uv_min, uv_max=uv_max, parent=uv_preview_drawlist)


def set_destination_uv(sender, app_data, user_data):
	global destination_id, atlas_destination, destination_uv_drawlist
	destination_id = user_data
	entry = aquatica[destination_id]
	draw_uv_preview(atlas_destination, COLOR_DEST, entry)
	dpg.delete_item(destination_uv_drawlist)
	uv_min = min(x for x, y in entry.corners), min(1-y for x, y in entry.corners)
	uv_max = max(x for x, y in entry.corners), max(1-y for x, y in entry.corners)
	destination_uv_drawlist = dpg.draw_image("atlas_texture", (256+20, 0), (512+20, 256), uv_min=uv_min, uv_max=uv_max, parent=uv_preview_drawlist)

with dpg.window(label="Source"):
	create_uv_listing(atlantica, atlantica_rows, "source", set_source_uv)

	for key in remapping:
		for text in atlantica_rows[key]:
			dpg.configure_item(text, color=(20, 255, 20, 255))

with dpg.window(label="Destination"):
	create_uv_listing(aquatica, aquatica_rows, "dest", set_destination_uv)

	for key in remapping.values():
		for text in aquatica_rows[key]:
			dpg.configure_item(text, color=(20, 255, 20, 255))

def delete_mapping_entry(sender, app_data, user_data):
	global remapping
	if remapping.get(user_data):
		del remapping[user_data]
		dpg.delete_item(dpg.get_item_parent(sender))

def preview_mapping_entry(sender, app_data, user_data):
	global remapping
	global source_uv_drawlist, destination_uv_drawlist
	if (dest := remapping.get(user_data)) is not None:
		draw_uv_preview(atlas_source, COLOR_SOURCE, atlantica[user_data])
		draw_uv_preview(atlas_destination, COLOR_DEST, aquatica[dest])

		dpg.delete_item(source_uv_drawlist)
		entry = atlantica[user_data]
		uv_min = min(x for x, y in entry.corners), min(1-y for x, y in entry.corners)
		uv_max = max(x for x, y in entry.corners), max(1-y for x, y in entry.corners)
		source_uv_drawlist = dpg.draw_image("atlas_texture", (0, 0), (256, 256), uv_min=uv_min, uv_max=uv_max, parent=uv_preview_drawlist)

		dpg.delete_item(destination_uv_drawlist)
		entry = aquatica[dest]
		uv_min = min(x for x, y in entry.corners), min(1-y for x, y in entry.corners)
		uv_max = max(x for x, y in entry.corners), max(1-y for x, y in entry.corners)
		destination_uv_drawlist = dpg.draw_image("atlas_texture", (256+20, 0), (512+20, 256), uv_min=uv_min, uv_max=uv_max, parent=uv_preview_drawlist)


entry_table = None

def create_mapping_entry(sender, app_data, user_data):
	global source_id, destination_id
	if source_id is None or destination_id is None:
		return
	
	if remapping.get(source_id):
		return
	
	remapping[source_id] = destination_id

	with dpg.table_row(parent=entry_table):
		dpg.add_button(label="Show", callback=preview_mapping_entry, user_data=source_id)
		dpg.add_button(label="Delete", callback=delete_mapping_entry, user_data=source_id)
		dpg.add_text(f"{source_id}")
		dpg.add_text(f"{destination_id}")

	for row in (atlantica_rows[source_id], aquatica_rows[destination_id]):
		for text in row:
			dpg.configure_item(text, color=(20, 255, 20, 255))

def save_to_file(sender, app_data, user_data):
	with open("uv_remap_TR020_TR060.json", "w", encoding="utf8") as f:
		json.dump(remapping, f)

with dpg.window(label="Remapping"):
	dpg.add_button(label="Add mapping", callback=create_mapping_entry)
	dpg.add_same_line()
	dpg.add_button(label="Save to file", callback=save_to_file)

	with dpg.table(header_row=True) as entry_table:
		dpg.add_table_column(label="Prev")
		dpg.add_table_column(label="Button")
		dpg.add_table_column(label="Source")
		dpg.add_table_column(label="Dest")

		for k, v in remapping.items():
			with dpg.table_row():
				dpg.add_button(label="Show", callback=preview_mapping_entry, user_data=k)
				dpg.add_button(label="Delete", callback=delete_mapping_entry, user_data=k)
				dpg.add_text(f"{k}")
				dpg.add_text(f"{v}")


dpg.create_viewport(title="UV inspector", width=1800, height=1200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(main_window, True)

while dpg.is_dearpygui_running():
	jobs = dpg.get_callback_queue() # retrieves and clears queue
	dpg.run_callbacks(jobs)
	dpg.render_dearpygui_frame()

dpg.destroy_context()
