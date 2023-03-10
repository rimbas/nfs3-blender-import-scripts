from typing import Self
from PIL import Image
import numpy as np
from pathlib import Path
from texture_packer import TexturePair

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
			self.atlas.atlas.paste(self.texture.albedo, self.corner)
			self.atlas.atlas_mask.paste(self.texture.mask, self.corner)
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
		self.atlas = Image.new("RGB", (size, size))
		self.atlas_mask = Image.new("L", (size, size))
		self.index = 0
		self.quadtree = QuadLeaf(self, size)
		self.packed = {}

	def pack(self, pair: TexturePair):
		if quad := self.quadtree.pack(pair):
			self.packed[pair] = quad
		return quad


track_id = "TR060"

atlas = AtlasPacker(track_id, 1024)
cutout_atlas = AtlasPacker(track_id, 512)

texture_pairs: list[TexturePair] = []

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

	if pair.is_cutout:
		if not cutout_atlas.pack(pair):
			raise Exception(f"Could not pack texture with id {texture_id}")


if __name__ == "__main__":
	atlas.atlas.save(f"{track_id}.png")
	atlas.atlas_mask.save(f"{track_id}-a.png")

	#cutout_atlas.atlas.save(f"{track_id}-cutout.png")
	#cutout_atlas.atlas_mask.save(f"{track_id}-cutout-a.png")

	#breakpoint

