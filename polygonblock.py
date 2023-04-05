from io import BytesIO
import numpy as np
from struct import unpack
from basic import *

class VertexOps:

	poly: list[PolygonData]
	
	def get_vertex_set(self):
		vertex_set = set()
		for polygon in self.poly:
			vertex_set.update(polygon.vertex)
		return vertex_set
	
	def to_mesh(self, vertex_buffer: np.ndarray, flipped=False, shading_buffer=None):
		vertex_set = list(self.get_vertex_set())
		vertices = vertex_buffer[vertex_set]
		if shading_buffer is not None:
			shading = shading_buffer[vertex_set]
		else:
			shading = None
		map = {v: i for i, v in enumerate(vertex_set)}

		polygons = np.zeros((len(self.poly), 4), dtype=np.uint32)
		textures = set()
		
		for i, p in enumerate(self.poly):
			if flipped:
				polygons[i] = (
					map[p.vertex[3]], 
					map[p.vertex[2]],
					map[p.vertex[1]],
					map[p.vertex[0]],
				)
			else:
				polygons[i] = [map[p.vertex[j]] for j in range(4)]
			textures.add(p.texture)

		pass

		return vertices, polygons, textures, shading
	
	def to_shading(self, shading_buffer: np.ndarray):
		vertex_set = list(self.get_vertex_set())
		#shading = np.array(shading_buffer[vertex_set], dtype=np.float32)
		#shading /= 255
		#return shading
		return shading_buffer[vertex_set]
	
	def iter_polys(self):
		yield from self.poly

class PolygonChunk(VertexOps):
	size: int
	poly: list[PolygonData] = []

	def __init__(self, data: BytesIO):
		self.size = unpack_one(data, 4, "l")
		if self.size > 0:
			sizedup = unpack_one(data, 4, "l")
			if self.size != sizedup:
				raise "Size mismatch"
			self.poly = [PolygonData.read(data) for i in range(self.size)]

	def polygons_to_triangle_buffer(self):
		#buffer = np.zeros((self.nVertices, 3), dtype=np.uint32)
		buffer = np.zeros((self.size * 2, 3), dtype=np.uint32)
		for i, polygon in enumerate(self.poly):
			buffer[i*2] = [polygon.vertex[0], polygon.vertex[1], polygon.vertex[2]]
			buffer[i*2+1] = [polygon.vertex[2], polygon.vertex[3], polygon.vertex[0]]

			if polygon.flags & 0x10:
				# double sided polygon
				pass

		return buffer
	
	def polygons_to_quad_buffer(self):
		#buffer = np.zeros((self.nVertices, 3), dtype=np.uint32)
		buffer = np.zeros((self.size, 4), dtype=np.uint32)
		for i, polygon in enumerate(self.poly):
			buffer[i] = [polygon.vertex[0], polygon.vertex[1], polygon.vertex[2], polygon.vertex[3]]

			if polygon.flags & 0x10:
				# double sided polygon
				pass

		return buffer

class PolyObjData(VertexOps):
	type: int
	numpoly: int
	poly: list[PolygonData] = []

	def __init__(self, data: BytesIO):
		self.type = unpack_one(data, 4, "l")
		if self.type == 1:
			self.numpoly = unpack_one(data, 4, "l")
			self.poly = [PolygonData.read(data) for i in range(self.numpoly)]
			pass

	def polygons_to_quad_buffer(self):
		buffer = np.zeros((self.numpoly, 4), dtype=np.uint32)
		for i, polygon in enumerate(self.poly):
			buffer[i] = [polygon.vertex[0], polygon.vertex[1], polygon.vertex[2], polygon.vertex[3]]

			if polygon.flags & 0x10:
				# double sided polygon
				pass

		return buffer


class ObjPolyBlock:
	nPolygons: int
	nObjects: int
	obj: list[PolyObjData] = []
	
	def __init__(self, data: BytesIO):
		self.nPolygons = unpack_one(data, 4, "l")
		if self.nPolygons > 0:
			self.nObjects = unpack_one(data, 4, "l")
			self.obj = [PolyObjData(data) for i in range(self.nObjects)]
		pass

	def iter_polys(self):
		for polyObj in self.obj:
			yield from polyObj.iter_polys()

class PolygonBlock:
	poly: list[PolygonChunk] # main road polygons
	obj: list[ObjPolyBlock] # scenery

	def __init__(self, data: BytesIO):
		"""
		poly[4] high resolution poly data
		poly[5] high resolution transparent stuff
		poly[6] road lanes
		"""
		self.poly = [PolygonChunk(data) for i in range(7)]
		self.obj = [ObjPolyBlock(data) for i in range(4)]
		pass

	def iter_polys(self):
		for i in range(4, 7):
			yield from self.poly[i].iter_polys()
		for obj in self.obj:
			yield from obj.iter_polys()
