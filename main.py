from frd import FRD
from frd_exporter import export

with open("TR06.FRD", "rb") as f:
	filedata = f.read()

aquatica = FRD(filedata)
export(aquatica, "aquatica.glb")

breakpoint
