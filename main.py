from frd import FRD

'''Utility script to view at runtime data in debugger'''

with open("TR02.FRD", "rb") as f:
	atlantica = FRD(f.read())

with open("TR06.FRD", "rb") as f:
	aquatica = FRD(f.read())

if __name__ == "__main__":
	#export(aquatica, "aquatica.glb")

	textures = aquatica.textures

	texture_set = aquatica.get_used_texture_set()

	breakpoint
