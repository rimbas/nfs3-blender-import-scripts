import os
from PIL import Image
import numpy as np

class TexturePair:

	albedo: Image
	mask: Image
	is_cutout: bool

	def __init__(self, albedo: Image, mask: Image):
		self.albedo = albedo
		self.mask = mask
		
		self.is_cutout = self.check_mask()

	def check_mask(self):
		data = np.array(self.mask)

		pass

