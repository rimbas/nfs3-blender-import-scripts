from pathlib import Path
from PIL import Image
import numpy as np

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

def gather_textures(track_folder):
	texture_pairs = []

	for texture_path in Path(track_folder).glob("*"):
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
	
	return texture_pairs
