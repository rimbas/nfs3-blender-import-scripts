from io import BytesIO, SEEK_SET, SEEK_CUR, SEEK_END
import numpy as np

from basic import *
from polygonblock import *
from struct import unpack

class FRD:

	nBlocks: int
	
	def __init__(self, data: bytes):
		bytes = BytesIO(data)

		# skip header
		bytes.seek(28, SEEK_SET)
		self.nBlocks = unpack("i", bytes.read(4))[0]
		#self.nBlocks = 0
		self.trk = [TrackBlock(bytes) for i in range(self.nBlocks+1)]
		self.poly = [PolygonBlock(bytes) for i in range(self.nBlocks+1)]
		self.xobj = [XobjBlock(bytes) for i in range(4*(self.nBlocks+1)+1)]
		self.nTextures = unpack("i", bytes.read(4))[0]
		self.textures = [TextureData.read(bytes) for i in range(self.nTextures)]
		pass

class TrackBlock:
	ptCentre: FloatPoint
	ptBounding: list[FloatPoint]
	nVertices: int
	nHiResVert: int
	nLoResVert: int
	nMedResVert: int
	nObjectVert: int

	def __init__(self, data: BytesIO):
		self.ptCentre = FloatPoint.read(data)
		self.ptBounding = [FloatPoint.read(data) for i in range(4)]

		self.nVertices = unpack_one(data, 4, "l")
		self.nHiResVert = unpack_one(data, 4, "l")
		self.nLoResVert = unpack_one(data, 4, "l")
		self.nMedResVert = unpack_one(data, 4, "l")
		self.nVerticesDup = unpack_one(data, 4, "l")
		self.nObjectVert = unpack_one(data, 4, "l")
		self.vertices = [FloatPoint.read(data) for i in range(self.nVertices)]
		self.shadingVertices = [VertexColor.read(data) for i in range(self.nVertices)]
		self.neighborData = [NeighborData.read(data) for i in range(0x12C)]

		self.nStartPosition = unpack_one(data, 4, "l")
		self.nPositions = unpack_one(data, 4, "l")
		self.nPolygons = unpack_one(data, 4, "l")
		self.nVroad = unpack_one(data, 4, "l")
		self.nXobj = unpack_one(data, 4, "l")
		self.nPolyObj = unpack_one(data, 4, "l")
		self.nSoundsrc = unpack_one(data, 4, "l")
		self.nLightsrc = unpack_one(data, 4, "l")
		
		self.positionData = [PositionData.read(data) for i in range(self.nPositions)]
		self.polyData = [PolyVroadData.read(data) for i in range(self.nPolygons)]
		self.vroadData = [VroadData.read(data) for i in range(self.nVroad)]
		self.xobj = [RefXobj.read(data) for i in range(self.nXobj)]
		checkpoint = data.tell()
		self.polyobj = [RefPolyObject.read(data) for i in range(self.nPolyObj)]
		data.seek(checkpoint + self.nPolyObj * 20, SEEK_SET)
		self.soundsrc = [Soundsrc.read(data) for i in range(self.nSoundsrc)]
		self.lightsrc = [Lightsrc.read(data) for i in range(self.nLightsrc)]
		pass

	def vertices_to_buffer(self):
		buffer = np.zeros((self.nVertices, 3), dtype=np.float32)
		for i, vertex in enumerate(self.vertices):
			buffer[i] = [vertex.x, vertex.y, vertex.z]
		return buffer

	def shading_to_buffer(self):
		buffer = np.zeros((self.nVertices, 4), dtype=np.uint8)
		for i, shading in enumerate(self.shadingVertices):
			buffer[i] = (shading.r, shading.g, shading.b, shading.a)
		return buffer


class XobjBlock:
	def __init__(self, data: BytesIO) -> None:
		self.nobj = unpack_one(data, 4, "l")
		self.obj = [XobjData(data) for i in range(self.nobj)]

class XobjData:
	def __init__(self, data: BytesIO) -> None:
		self.type = unpack_one(data, 4, "l")
		if self.type == 4:
			# static extra-object
			self.crossno = unpack_one(data, 4, "l")
			data.seek(4, SEEK_CUR) # unknown
			self.pointReference = FloatPoint.read(data)
			data.seek(4, SEEK_CUR) # unknown
			self.nVertices = unpack_one(data, 4, "l")
			self.vertices = [FloatPoint.read(data) for i in range(self.nVertices)]
			self.shadingVertices = [VertexColor.read(data) for i in range(self.nVertices)]
			self.nPolygons = unpack_one(data, 4, "l")
			self.polyData = [PolygonData.read(data) for i in range(self.nPolygons)]
		elif self.type == 3:
			# animated extra object
			self.crossno = unpack_one(data, 4, "l")
			data.seek(4, SEEK_CUR) # long unknown
			data.seek(2*9, SEEK_CUR) # short unknown[9]
			self.type3 = unpack_one(data, 1, "B")
			if self.type3 != 3:
				raise Exception("Wrong type3 for animated extra object")
			self.objno = unpack_one(data, 1, "B")
			self.nAnimLength = unpack_one(data, 2, "h")
			data.seek(2, SEEK_CUR) # short unknown
			self.animData = [AnimData.read(data) for i in range(self.nAnimLength)]
			self.nVertices = unpack_one(data, 4, "l")
			self.vertices = [FloatPoint.read(data) for i in range(self.nVertices)]
			self.shadingVertices = [VertexColor.read(data) for i in range(self.nVertices)]
			self.nPolygons = unpack_one(data, 4, "l")
			self.polyData = [PolygonData.read(data) for i in range(self.nPolygons)]
		else:
			raise "Unknown extra object type"
