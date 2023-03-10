from itertools import chain
import json
import drawsvg as draw
from basic import TextureData
from frd import FRD
from main import aquatica
from texture_analyser import AtlasPacker, atlas

def texture_atlas_svg(atlas: AtlasPacker, frd: FRD, /, filename=f"{atlas.name}.svg"):
	"""level texture data overlaid on a packed atlas"""

	d = draw.Drawing(atlas.size, atlas.size)

	atlas_texture = {t.id: t for t in atlas.packed}
	used_textures = frd.get_used_texture_set()

	d.append(draw.Image(0, 0, atlas.size, atlas.size, "TR060.png", embed=False))

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

		corners = [(qx + x * size, qy + y * size) for x, y in uvs]

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

def atlas_preview(atlas: AtlasPacker, /, filename=f"{atlas.name}.svg"):
	"""packed atlas overlay"""
	d = draw.Drawing(atlas.size, atlas.size)

	atlas_texture = {t.id: t for t in atlas.packed}

	d.append(draw.Image(0, 0, atlas.size, atlas.size, "TR060.png", embed=False))

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

def atlas_mapping(atlas: AtlasPacker, frd: FRD, /, filename=f"{atlas.name}.json"):

	atlas_texture = {t.id: t for t in atlas.packed}
	used_textures = frd.get_used_texture_set()

	mapping: dict[int, list[float]] = {}

	#for texture, quad in atlas.packed.items():
	for i, texture in enumerate(frd.textures):
		if i not in used_textures:
			continue

		texture_id = texture.texture
		texture_pair = atlas_texture[texture_id]
		quad = atlas.packed[texture_pair]
		
		qx, qy = quad.corner
		#size = quad.size
		size = texture_pair.width / atlas.size

		corners =[((qx + x * size)/atlas.size, (qy + y * size)/atlas.size) for x, y in texture.uv_pairs()]
		mapping[i] = corners

	with open(filename, "w", encoding="utf8") as f:
		json.dump(mapping, f)

if __name__ == "__main__":
	#texture_atlas_svg(atlas, aquatica, filename=f"{atlas.name}v2.svg")
	atlas_mapping(atlas, aquatica, filename=f"{atlas.name}-uv_mapping.json")
