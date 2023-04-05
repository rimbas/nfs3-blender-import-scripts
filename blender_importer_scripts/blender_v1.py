# This stub runs a python script relative to the currently open
# blend file, useful when editing scripts externally.

import bpy
import bmesh
import sys
import os
import numpy as np

directory = os.path.dirname(bpy.data.filepath)

if not dir in sys.path:
    sys.path.append(directory)

import frd

if __name__ == "__main__":
    
    """Imports FRD as meshes. Creates individual materials for each texture"""

    track_name = "TR06"
    
    print("-------------------------------------------------------------------------------")
    
    with open(os.path.join(directory, f"{track_name}.FRD"), "rb") as f:
        filedata = f.read()
        
        nfs_track = frd.FRD(filedata)
        
        if f"{track_name}" in bpy.data.collections:
            col = bpy.data.collections.get(f"{track_name}")
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)
        
        scene = bpy.context.scene
        col = bpy.data.collections.new(f"{track_name}")
        scene.collection.children.link(col)
        
        # generate material slots
        material_mapping = {}
        texture_files = set(t.texture for t in nfs_track.textures)
        for texture_id in texture_files:
            material_name = f"{track_name}_{texture_id:04}"
            
            if material_name in bpy.data.materials:
                material_mapping[texture_id] = bpy.data.materials[material_name]
            else:
                imgname = f"{texture_id:04}"
                if imgname in bpy.data.images:
                    img = bpy.data.images[imgname]
                else:
                    imgpath = os.path.join(directory, f"{track_name}0", f"{imgname}.BMP")
                    img = bpy.data.images.load(imgpath)
                
                maskname = f"{texture_id:04}"
                if maskname in bpy.data.images:
                    mask = bpy.data.images[maskname]
                else:
                    maskpath = os.path.join(directory, f"{track_name}0", f"{maskname}-a.BMP")
                    mask = bpy.data.images.load(maskpath)
                
                material = bpy.data.materials.new(name=material_name)
                material_mapping[texture_id] = material
                material.use_fake_user = True
                material.use_nodes = True

                material_output = material.node_tree.nodes.get("Material Output")
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                
                tex_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                tex_node.image = img
                
                mask_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                mask_node.image = mask
                
                material.node_tree.links.new(tex_node.outputs[0], principled_bsdf.inputs[0])
                material.node_tree.links.new(mask_node.outputs[0], principled_bsdf.inputs[21])
            
        #print(list(material_mapping.items()))
        
        for i in range(nfs_track.nBlocks+1):
            if i == 0: continue
            track = nfs_track.trk[i]
            polyblock = nfs_track.poly[i]
            polymesh, transparent, lanes = polyblock.poly[4], polyblock.poly[5], polyblock.poly[6]
            
            """if False:
                bpy.ops.object.empty_add(type="PLAIN_AXES", location=(track.ptCentre.x, track.ptCentre.y, track.ptCentre.z))
                empty = bpy.context.view_layer.objects.active
                empty.name = f"track_{i:04}_origin"
                scene.collection.objects.unlink(empty)
                col.objects.link(empty)"""

            vertex_buffer = track.vertices_to_buffer()
            shading_buffer = track.shading_to_buffer()
            shading = polymesh.to_shading(shading_buffer)
            
            def create_object(object_name, mesh_object):
                verts, polys, textures = mesh_object.to_mesh(vertex_buffer)
                mesh = bpy.data.meshes.new(object_name)
                obj = bpy.data.objects.new(object_name, mesh)
                material_index_mapping = {}
                for material_index, tex_id in enumerate(textures):
                    obj.data.materials.append(material_mapping.get(tex_id))
                    material_index_mapping[tex_id] = material_index
                    
                print(object_name)
                print(textures)
                print(list(obj.data.materials))
                print(list(material_index_mapping.items()))
                col.objects.link(obj)
                mesh.from_pydata(verts, [], polys)
                mesh.uv_layers.new(name="UVMap")
                
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.faces.ensure_lookup_table()
                uv_layer = bm.loops.layers.uv[0]
                
                for polygon_index, polygon in enumerate(mesh_object.poly):
                    face = bm.faces[polygon_index]
                    face.material_index = material_index_mapping[polygon.texture]
                    #for loop in face.loops:
                    #    print(loop)
                    #    break
                    #break
                    
                bm.to_mesh(mesh)
                bm.free()
                    
            
            #create_object(f"track_{i:04}_hires", polymesh)
            
            if transparent.size > 0:
                create_object(f"track_{i:04}_transparent", transparent)
                
            if lanes.size > 0:
                pass
                #create_object(f"track_{i:04}_lanes", lanes)
            
            index = 0
            for objPolyBlock in polyblock.obj:
                if objPolyBlock.nPolygons > 0:
                    for polyObjData in objPolyBlock.obj:
                        if polyObjData.type == 1:
                            create_object(f"track_{i:04}_poly_{index:02}", polyObjData)
                            index += 1
                            break
                                
            break
        pass
