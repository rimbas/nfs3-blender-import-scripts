from frd import FRD
import pygltflib as gltf

def export_gltf(frd: FRD, filename: str):

	g = gltf.GLTF2()

	scene = gltf.Scene()
	gltf.scenes.append(scene)

	for i in range(frd.nBlocks):
		node = gltf.Node()
		scene.nodes.append(node)

		track = frd.trk[i]
		polyblock = frd.poly[i]
		mesh = polyblock.poly[4]
		transparent = polyblock.poly[5]
		lanes = polyblock.poly[6]

		vertex_buffer = track.vertices_to_buffer()
		triangle_buffer = mesh.quads_to_buffer()

		pass

def export(frd: FRD, filename: str):

	for i in range(frd.nBlocks):

		track = frd.trk[i]
		polyblock = frd.poly[i]
		mesh = polyblock.poly[4]
		transparent = polyblock.poly[5]
		lanes = polyblock.poly[6]

		vertex_buffer = track.vertices_to_buffer()
		shading_buffer = track.shading_to_buffer()
		triangle_buffer = mesh.polygons_to_quad_buffer()

		verts, polys, texture = mesh.to_mesh(vertex_buffer)
		shading = mesh.to_shading(shading_buffer)

		pass

		
