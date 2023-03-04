import bpy
from frd import FRD

def read_some_data(context, filepath, use_some_setting):
	f = open(filepath, 'rb')
	data = f.read()
	f.close()

	# would normally load the data here
	print(data)

	structure = FRD(data)
	print(structure)

	return {'FINISHED'}

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportFRD(Operator, ImportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "import_frd.import_file"  # important since its how bpy.ops.import_test.some_data is constructed
	bl_label = "Import Need for Speed 3 track"

	# ImportHelper mixin class uses this
	filename_ext = ".frd"

	filter_glob: StringProperty(
		default="*.frd",
		options={'HIDDEN'},
		maxlen=255,  # Max internal buffer length, longer would be clamped.
	)

	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.
	use_setting: BoolProperty(
		name="Import external data",
		description="Import external track models and textures",
		default=False,
	)

	def execute(self, context):
		return read_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportFRD.bl_idname, text="Import Need for Speed 3 track")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
	bpy.utils.register_class(ImportFRD)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
	bpy.utils.unregister_class(ImportFRD)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
	register()

	# test call
	#bpy.ops.import_frd.import_file('INVOKE_DEFAULT')
