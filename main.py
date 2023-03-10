from frd import FRD
from texture_analyser import atlas

with open("TR02.FRD", "rb") as f:
	filedata = f.read()
	atlantica = FRD(filedata)

with open("TR06.FRD", "rb") as f:
	filedata = f.read()
	aquatica = FRD(filedata)


if __name__ == "__main__":
	#export(aquatica, "aquatica.glb")

	textures = aquatica.textures

	texture_set = aquatica.get_used_texture_set()

	breakpoint
