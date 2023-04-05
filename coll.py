from io import BytesIO, SEEK_SET, SEEK_CUR, SEEK_END
from basic import *
from polygonblock import VertexOps

# untested

class ColFile:
	
	def __init__(self, data: BytesIO) -> None:
		data.seek(4, SEEK_SET)
		self.version = unpack_one(data, 4, "l")
		self.fileLength = unpack_one(data, 4, "l")
		self.nBlocks = unpack_one(data, 4, "l")
		self.xbTable = list(range(self.nBlocks))

class XBColBlock:
	
	def __init__(self, data: BytesIO) -> None:
		self.size = unpack_one(data, 4, "l")
		self.xbid = unpack_one(data, 2, "h")
		self.nrec = unpack_one(data, 2, "h")
		match (self.xbid):
			case 2:
				t = ColTextureInfo
			case 8:
				t = ColVertex
			case 7 | 18:
				t = ColObject
			case 15:
				t = ColVroad
		self.data = [t.read(data) for i in range(self.nrec)]


@dataclass(frozen=True)
class ColTextureInfo:
	texture: int # texture id in QFS file
	unknown1: int
	unknown2: int
	unknown3: int

	@staticmethod
	def read(data: BytesIO):
		return ColTextureInfo(*unpack("hhhh", data.read(8)))

@dataclass(frozen=True)
class ColVertex:

	point: FloatPoint
	unknown: int

	@staticmethod
	def read(data: BytesIO):
		return ColVertex(FloatPoint.read(data), *unpack("l", data.read(4)))

@dataclass(frozen=True)
class ColPolygon:
	texture: int
	vertex: tuple[int]

	@staticmethod
	def read(data: BytesIO):
		return ColPolygon(*unpack("h", data.read(2)), unpack("BBBB", data.read(4)))

class ColStruct3D(VertexOps):
	def __init__(self, data: BytesIO) -> None:
		self.size = unpack_one(data, 4, "l")
		self.nVertices = unpack_one(data, 2, "h")
		self.nPoly = unpack_one(data, 2, "h")
		self.vertices = [ColVertex.read(data) for i in range(self.nVertices)]
		self.poly = [ColVertex.read(data) for i in range(self.nVertices)]
	
	@staticmethod
	def read(data: BytesIO):
		return ColStruct3D(data)


class ColObject:
	def __init__(self, data: BytesIO) -> None:
		self.size = unpack_one(data, 2, "h")
		if self.size == 16:
			self.type = unpack_one(data, 1, "B")
			self.struct3D = unpack_one(data, 1, "B")
			self.point = IntPoint.read(data)
		else:
			self.type = unpack_one(data, 1, "B")
			if self.type != 3:
				raise Exception(f"Unknown animate ColObject type \"{self.type}\"")
			self.struct3D = unpack_one(data, 1, "B")
			self.animLength = unpack_one(data, 2, "h")
			self.unknown = unpack_one(data, 2, "h")
			self.animData = [AnimData.read(data) for i in range(self.animLength)]

	@staticmethod
	def read(data):
		return ColObject(data)

@dataclass(frozen=True)
class ColVector:
	'''Normalized vector'''
	x: int
	z: int
	y: int
	unused: int

	@staticmethod
	def read(data: BytesIO):
		return ColVector(*unpack("BBBB", data.read(4)))

class ColVroad:
	def __init__(self, data: BytesIO) -> None:
		self.point = IntPoint.read(data)
		self.unknown = unpack_one(data, 4, "l")
		self.normal = ColVector.read(data)
		self.forward = ColVector.read(data)
		self.right = ColVector.read(data)
		self.leftWall = unpack_one(data, 4, "l")
		self.rightWall = unpack_one(data, 4, "l")
	
	@staticmethod
	def read(data: BytesIO):
		return ColVroad(data)