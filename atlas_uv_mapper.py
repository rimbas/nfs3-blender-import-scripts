#!/usr/bin/env python

from dataclasses import dataclass
import json
import drawsvg as draw
from frd import FRD
from quad_packer import AtlasPacker, make_atlas

def texture_atlas_svg(atlas: AtlasPacker, frd: FRD, /, filename, sx=0.0, sy=0.0):
	"""level texture data overlaid on a packed atlas"""

	d = draw.Drawing(atlas.size, atlas.size)

	atlas_texture = {t.id: t for t in atlas.packed}
	used_textures = frd.get_used_texture_set()
	sx *= atlas.size
	sy *= atlas.size

	d.append(draw.Image(0, 0, atlas.size, atlas.size, f"{atlas.name}.png", embed=False))

	#for texture, quad in atlas.packed.items():
	for i, texture in enumerate(frd.textures):
		if i not in used_textures:
			continue

		texture_id = texture.texture
		texture_pair = atlas_texture[texture_id]
		quad = atlas.packed[texture_pair]

		qx, qy = quad.corner
		#size = quad.size
		size = texture_pair.width
		uvs = texture.uv_pairs()

		irregular = False
		color_stroke = "green"
		if max(texture.corners) > 1 or min(texture.corners) < 0:
			color_stroke = "red"
			irregular = True

		corners = [(qx + x * size + sx, qy + y * size + sy) for x, y in uvs]

		center = (corners[0][0] + corners[2][0]) / 2, (corners[0][1] + corners[2][1]) / 2
	
		p = draw.Path(stroke_width=1, stroke=color_stroke, fill="none")

		#p.M(qx + corners[0][0], qy + corners[0][1])
		p.M(*corners[0])
		p.L(*corners[1])
		p.L(*corners[2])
		p.L(*corners[3])
		p.Z()
		d.append(p)

		text_props = dict(dominant_baseline='middle', text_anchor='middle')
		#d.append(draw.Text(f"{i}\n{texture_id}", 8, *center, fill="none", stroke="black", **text_props))
		d.append(draw.Text(f"{i}\n{texture_id}", 8, *center, fill="white", **text_props))

		pass

	d.save_svg(filename)

def atlas_preview(atlas: AtlasPacker, /, filename):
	"""packed atlas overlay"""
	d = draw.Drawing(atlas.size, atlas.size)

	atlas_texture = {t.id: t for t in atlas.packed}

	d.append(draw.Image(0, 0, atlas.size, atlas.size, f"{atlas.name}.png", embed=False))

	#for texture, quad in atlas.packed.items():
	for pair, quad in atlas.packed.items():
		texture_id = pair.id
		size = pair.width

		qx1, qy1 = quad.corner
		qx2, qy2 = qx1 + size, qy1 + size

		center = (qx1 + qx2) // 2+4, (qy1 + qy2) // 2+4
		
		#p = draw.Path(stroke_width=1, stroke="green", fill="none")
		#d.append(p)

		d.append(draw.Text(f"{texture_id}", 8, *center, fill="none", stroke="black", dominant_baseline='middle', text_anchor='middle'))
		d.append(draw.Text(f"{texture_id}", 8, *center, fill="white", stroke="none", dominant_baseline='middle', text_anchor='middle'))

	d.save_svg(filename)

@dataclass
class TextureUvEntry:
	corners: list[list[float]]
	x: int
	y: int
	atlas_size: int
	texture_size: int
	id: int

def atlas_mapping(atlas: AtlasPacker, frd: FRD, /, filename, sy=0.0):

	atlas_texture = {t.id: t for t in atlas.packed}
	used_textures = frd.get_used_texture_set()

	mapping = {}

	#for texture, quad in atlas.packed.items():
	for i, texture in enumerate(frd.textures):
		if i not in used_textures:
			continue

		texture_id = texture.texture
		texture_pair = atlas_texture[texture_id]
		quad = atlas.packed[texture_pair]
		
		qx, qy = quad.corner
		#size = quad.size
		size = texture_pair.width

		corners =[(((qx + x * size)/atlas.size), (1.0-((qy + y * size)/atlas.size))-sy) for x, y in texture.uv_pairs()]
		mapping[i] = {
			"corners": corners,
			"x": qx,
			"y": qy,
			"atlas_size": atlas.size,
			"texture_size": texture_pair.width,
			"id": texture_pair.id,
		}

	with open(filename, "w", encoding="utf8") as f:
		json.dump(mapping, f)

	pass



if __name__ == "__main__":
	import sys, os, argparse
	parser = argparse.ArgumentParser(
		prog="atlas_uv_mapper",
		description="Maps texture UVs to an atlas",
	)
	parser.add_argument("track_id")
	parser.add_argument("atlas_size", type=int)
	parser.add_argument("frd_file")

	parser.add_argument("--shift-y", type=float, default=0.0)

	args = parser.parse_args()
	
	atlas_size = args.atlas_size
	track_id = args.track_id
	frd_filename = args.frd_file
	
	if os.path.isfile(frd_filename):
		with open(frd_filename, "rb") as f:
			frd = FRD(f.read())
	else:
		print(f"Unable to find FRD file \"{frd_filename}\"")
		sys.exit(1)

	# 1024
	atlas = make_atlas(track_id, atlas_size)

	atlas.image.save(f"{track_id}.png")
	atlas.image_mask.save(f"{track_id}-a.png")
	atlas_mapping(atlas, frd, filename=f"{track_id}-uv_mapping.json", sy=args.shift_y)
	texture_atlas_svg(atlas, frd, filename=f"{track_id}-mapping.svg", sy=args.shift_y)

