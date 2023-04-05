from io import BytesIO
from dataclasses import dataclass
from struct import unpack
from enum import Enum

class PolygonType(Enum):
	TRACK = 0
	TRANSPARENT = 1
	LANES = 2
	OBJECT = 3
	EXTRAOBJECT = 4

def unpack_one(data: BytesIO, length: int, pattern: str):
	return unpack(pattern, data.read(length))[0]

@dataclass(frozen=True)
class FloatPoint:
	x: float
	z: float
	y: float

	@staticmethod
	def read(data: BytesIO):
		return FloatPoint(*unpack("fff", data.read(12)))

@dataclass(frozen=True)
class IntPoint:
	"""
	Is integer only when stored
	Divide by 2^16 to get floating point value
	"""
	x: int
	z: int
	y: int

	@staticmethod
	def read(data: BytesIO):
		i = unpack("iii", data.read(12))
		return IntPoint(i[0] / 2**16, i[1] / 2**16, i[2] / 2**16)

@dataclass(frozen=True)
class VertexColor:
	b: int
	g: int
	r: int
	a: int

	@staticmethod
	def read(data: BytesIO):
		return VertexColor(*unpack("BBBB", data.read(4)))

@dataclass(frozen=True)
class PolygonData:
	"""
	size: 14 bytes
	"""
	vertex: tuple[int]
	texture: int
	unknown: int
	flags: int
	unknown2: int

	@staticmethod
	def read(data: BytesIO):
		vertices = unpack("hhhh", data.read(8))
		other = unpack("hhBB", data.read(6))
		return PolygonData(vertices, *other)
	
	@property
	def doublesided(self):
		return self.flags & 0x10

@dataclass
class NeighborData:
	"""
	size: 4 bytes
	"""
	block: int

	@staticmethod
	def read(data: BytesIO):
		return NeighborData(*unpack("hxx", data.read(4)))

@dataclass(frozen=True)
class PositionData:
	"""
	size: 8 bytes
	"""
	polygon: int
	nPolygons: int
	extraNeighbor1: int
	extraNeighbor2: int

	@staticmethod
	def read(data: BytesIO):
		return PositionData(*unpack("hBxhh", data.read(8)))

@dataclass(frozen=True)
class PolyVroadData:
	vroadEntry: int
	flags: int

	@staticmethod
	def read(data: BytesIO):
		return PolyVroadData(*unpack("BBxxxxxx", data.read(8)))
	
@dataclass(frozen=True)
class VroadData:
	xNorm: int
	zNorm: int
	yNorm: int
	xForw: int
	zForw: int
	yForw: int

	@staticmethod
	def read(data: BytesIO):
		return VroadData(*unpack("hhhhhh", data.read(12)))

@dataclass(frozen=True)
class RefXobj:
	point: IntPoint
	globalno: int
	crossindex: int

	@staticmethod
	def read(data: BytesIO):
		return RefXobj(IntPoint.read(data), *unpack("xxhxxBx", data.read(8)))

@dataclass(frozen=True)
class RefPolyObject:
	entrysize: int
	type: int
	no: int
	point: IntPoint
	crossindex: int

	@staticmethod
	def read(data: BytesIO):
		entrysize = unpack("h", data.read(2))[0]

		if entrysize == 16:
			return RefPolyObject(entrysize, *unpack("BB", data.read(2)), IntPoint.read(data), -1)
		elif entrysize == 20:
			return RefPolyObject(entrysize, *unpack("BB", data.read(2)), IntPoint.read(data), *unpack("i", data.read(4)))
		else:
			raise "Unexpected entry size"

@dataclass(frozen=True)
class Soundsrc:
	refpoint: IntPoint
	type: int

	@staticmethod
	def read(data: BytesIO):
		return Soundsrc(IntPoint.read(data), *unpack("i", data.read(4)))
	
@dataclass(frozen=True)
class Lightsrc:
	refpoint: IntPoint
	type: int

	@staticmethod
	def read(data: BytesIO):
		return Lightsrc(IntPoint.read(data), *unpack("i", data.read(4)))

@dataclass(frozen=True)
class AnimData:
	"""size: 20 bytes"""
	point: IntPoint
	costheta: float
	sintheta: float

	@staticmethod
	def read(data: BytesIO):
		return AnimData(IntPoint.read(data), *unpack("ff", data.read(8)))

@dataclass(frozen=True)
class TextureData:
	"""size: 47 bytes"""
	width: int
	height: int
	unknown: int
	corners: tuple[float]
	unknown2: int
	isLane: int
	texture: int

	@staticmethod
	def read(data: BytesIO):
		dim = unpack("hhl", data.read(8))
		corners = unpack("ffffffff", data.read(4*8))
		unk2 = unpack("l", data.read(4))
		isLane = unpack("?", data.read(1))
		texture = unpack("h", data.read(2))
		return TextureData(*dim, corners, *unk2, *isLane, *texture)

	def uv_pairs(self):
		return [(self.corners[i*2], self.corners[i*2+1]) for i in range(4)]
	
	def convert_obj(self):
		uvs = self.uv_pairs()
		return [(1.0 - uv[0], 1.0 - uv[1]) for uv in uvs]
	
	def convert_xobj(self):
		uvs = self.uv_pairs()
		return [(uv[0], 1.0 - uv[1]) for uv in uvs]