#!/usr/bin/env python

import os
import json
from typing import Self
from PIL import Image
import numpy as np
from pathlib import Path

class TexturePair:

	id: int
	albedo: Image
	mask: Image
	is_cutout: bool
	size: tuple[int, int]
	width: int
	height: int
	ex_height: int
	ex_width: int
	shift_x = 0
	shift_y = 0

	def __init__(self, texture_id: int, albedo: Image, mask: Image):
		self.id = texture_id
		self.albedo = albedo
		self.mask = mask.convert("L")
		self.size = albedo.size
		self.width, self.height = albedo.width, albedo.height
		self.ex_width, self.ex_height = albedo.width, albedo.height

		self.is_cutout = self.check_mask()

	def check_mask(self):
		data = np.array(self.mask)

		if data.min() < data.max():
			return True
		return False


class QuadLeaf:
	atlas: 'AtlasPacker'
	texture: TexturePair
	leaves: dict[int, Self] = {}
	corner: tuple[int, int]
	size: int
	
	def __init__(self, atlas, size, index=0, parent=None) -> None:
		self.atlas = atlas
		self.size = size
		self.index = index
		self.parent = parent
		self.corner = self.get_coords()
		if size > 8:
			self.leaves = {i: QuadLeaf(atlas, self.size // 2, i, self) for i in range(4)}
		self.free = True
		self.dirty = False
	
	def __str__(self) -> str:
		return f"<QuadLeaf size={self.size} index={self.index} free={self.free} dirty={self.dirty} corner={self.corner}>"
	
	def __repr__(self) -> str:
		return str(self)

	def get_coords(self):
		bx, by = self.quarter()
		if self.parent:
			return self.parent.corner[0] + bx, self.parent.corner[1] + by
		return bx, by

	def quarter(self):
		s = self.size
		match (self.index):
			case 0:
				return (0, 0)
			case 1:
				return (s, 0)
			case 2:
				return (0, s)
			case 3:
				return (s, s)
			
	def pack(self, texture: TexturePair) -> Self|None:
		size = texture.width

		if not self.free:
			return
		elif self.size < size:
			return
		elif (self.size == size and not self.dirty) or not self.leaves:
			self.free = False
			self.texture = texture
			self.dirty = True
			self.atlas.image.paste(self.texture.albedo, self.corner)
			self.atlas.image_mask.paste(self.texture.mask, self.corner)
			return self

		for quad in self.leaves.values():
			if packed_quad := quad.pack(texture):
				self.dirty = True
				return packed_quad

		return

class AtlasPacker:
	packed: dict[TexturePair, QuadLeaf]

	def __init__(self, name: str, size: int):
		self.name = name
		self.size = size
		self.image = Image.new("RGB", (size, size))
		self.image_mask = Image.new("L", (size, size))
		self.index = 0
		self.quadtree = QuadLeaf(self, size)
		self.packed = {}

	def pack(self, pair: TexturePair):
		if quad := self.quadtree.pack(pair):
			self.packed[pair] = quad
		return quad

def make_atlas(track_id, atlas_size):
	atlas = AtlasPacker(track_id, atlas_size)
	#cutout_atlas = AtlasPacker(track_id, 512)

	texture_pairs: list[TexturePair] = []

	if not os.path.isdir(track_id):
		raise Exception(f"Directory \"{track_id}\" doesn't exist")

	for texture_path in Path(track_id).glob("*"):
		if texture_path.stem.endswith("-a"):
			continue
		elif texture_path.suffix.lower() != ".bmp":
			continue

		texture_id = int(texture_path.stem)

		pair = TexturePair(
			texture_id,
			Image.open(texture_path),
			Image.open(texture_path.with_stem(f"{texture_path.stem}-a"))
		)
		texture_pairs.append(pair)
		
		if not atlas.pack(pair):
			#raise Exception(f"Could not pack texture with id {texture_id}")
			raise Exception(f"Could not pack texture with id {texture_id}")

		# if pair.is_cutout:
		# 	if not cutout_atlas.pack(pair):
		# 		raise Exception(f"Could not pack texture with id {texture_id}")
		
	return atlas

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(
		prog="quad_packer",
		description="packs a directory of textures into an atlas",
	)

	parser.add_argument("directory")
	parser.add_argument("atlas_size", type=int)
	parser.add_argument("-u", "--uv-map", action="store_true")

	args = parser.parse_args()

	track_id = args.directory
	atlas_size = int(args.atlas_size)
	#print("No track ID given")
	#sys.exit(0)

	atlas = make_atlas(track_id, atlas_size)

	atlas.image.save(f"{track_id}.png")
	atlas.image_mask.save(f"{track_id}-a.png")

	if args.uv_map:
		
		mapping = {}

		for pair, quad in atlas.packed.items():
			texture_id = pair.id
			size = pair.width

			qx1, qy1 = quad.corner
			qx2, qy2 = qx1 + size, qy1 + size
			qx1, qy1, qx2, qy2 = qx1 / atlas_size, qy1 / atlas_size, qx2 / atlas_size, qy2 / atlas_size

			corners = [
				[qx1, 1-qy1],
				[qx2, 1-qy1],
				[qx2, 1-qy2],
				[qx1, 1-qy2],
			]

			mapping[texture_id] = {
				"corners": corners,
				"x": qx1,
				"y": qy1,
				"atlas_size": atlas.size,
				"texture_size": size,
				"id": texture_id,
			}

		with open(f"{track_id}-uv_mapping.json", "w", encoding="utf8") as f:
			json.dump(mapping, f)

	#cutout_atlas.atlas.save(f"{track_id}-cutout.png")
	#cutout_atlas.atlas_mask.save(f"{track_id}-cutout-a.png")

	#breakpoint

