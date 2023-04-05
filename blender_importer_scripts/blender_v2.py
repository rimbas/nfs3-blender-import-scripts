# This stub runs a python script relative to the currently open
# blend file, useful when editing scripts externally.

import bpy
from bpy import context
import bmesh
import sys
import os
import json
from importlib import reload
import numpy as np

directory = os.path.dirname(bpy.data.filepath)

if not dir in sys.path:
    sys.path.append(directory)

import frd
from basic import PolygonType

if __name__ == "__main__":
        
    track_name = "TR02"
    
    print("-------------------------------------------------------------------------------")
    
    with open(os.path.join(directory, f"{track_name}0-uv_mapping.json"), "r", encoding="utf8") as f:
        atlasMapping = json.load(f)
        atlasMapping = {int(k): v for k, v in atlasMapping.items()}
            
    with open(os.path.join(directory, f"{track_name}.FRD"), "rb") as f:
        filedata = f.read()
        
    nfs_track = frd.FRD(filedata)
    texture_list = nfs_track.textures
    
    if f"{track_name}" in bpy.data.collections:
        col = bpy.data.collections.get(f"{track_name}")
        for obj in col.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
    
    scene = bpy.context.scene
    col = bpy.data.collections.new(f"{track_name}")
    scene.collection.children.link(col)
    
    track_material = bpy.data.materials[f"{track_name}_atlas"]
    lane_material = bpy.data.materials["lanes"]
    
    def create_object(object_name, object_type, vertex_buffer, mesh_object, /, reference_point=None, origin=None):
        
        match (object_type):
            case PolygonType.TRACK:
                flipped_quads = True
            case _:
                flipped_quads = False
        
        verts, polys, textures = mesh_object.to_mesh(vertex_buffer, flipped_quads)
                
        mesh = bpy.data.meshes.new(object_name)
        obj = bpy.data.objects.new(object_name, mesh)
        match object_type:
            case PolygonType.LANES:
                obj.data.materials.append(lane_material)
            case _:
                obj.data.materials.append(track_material)
                
        if reference_point is not None:
            verts -= reference_point
            obj.location = reference_point
        elif origin:
            obj.location = origin

        col.objects.link(obj)
        mesh.from_pydata(verts, [], polys)
        mesh.uv_layers.new(name="UVMap")

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv[0]
                        
        for polygon_index, polygon in enumerate(mesh_object.poly):
            face = bm.faces[polygon_index]
                                
            mapped = atlasMapping.get(polygon.texture)
            corners = mapped["corners"]
            textureBlock = texture_list[polygon.texture]
                        
            match object_type: 
                case PolygonType.TRACK:
                    uvs = textureBlock.uv_pairs()
                    #corners = [corners[0],corners[1],corners[2],corners[3]]
                    corners = [corners[3],corners[2],corners[1],corners[0]]
                    #corners[0][0], corners[1][0] = corners[1][0], corners[0][0]
                    #corners[2][0], corners[3][0] = corners[3][0], corners[2][0]
                case PolygonType.OBJECT:
                    uvs = textureBlock.convert_xobj()
                case PolygonType.EXTRAOBJECT:
                    corners = [corners[1],corners[0],corners[3],corners[2]]
                case _:
                    uvs = textureBlock.uv_pairs()
            
            #uvs = [(x, 1.0-y) for x, y in corners]
            
            for i, loop in enumerate(face.loops):
                loop[uv_layer].uv = corners[i]
            
            face.material_index = 0
            match (object_type):
                case PolygonType.TRACK:
                    pass
                case PolygonType.EXTRAOBJECT:
                    pass
                case _:
                    face.normal_flip()

            #break
            
        bm.to_mesh(mesh)
        bm.free()

        return obj
    
    for i in range(nfs_track.nBlocks+1):
        #break
        #if i != 129: continue
        if i != 0: continue
        track = nfs_track.trk[i]
        center = np.array([track.ptCentre.x, track.ptCentre.y, track.ptCentre.z])
        polyblock = nfs_track.poly[i]
        polymesh, transparent, lanes = polyblock.poly[4], polyblock.poly[5], polyblock.poly[6]
        
        vertex_buffer = track.vertices_to_buffer()
                
        create_object(f"track_{i:04}_hires", PolygonType.TRACK, vertex_buffer, polymesh, reference_point=center)
        
        if transparent.size > 0:
            create_object(f"track_{i:04}_transparent", PolygonType.TRANSPARENT, vertex_buffer, transparent, reference_point=center)
            pass
            
        if lanes.size > 0:
            create_object(f"track_{i:04}_lanes", PolygonType.LANES, vertex_buffer, lanes, reference_point=center)
            pass
        
        index = 0
        for objPolyBlock in polyblock.obj:
            if objPolyBlock.nPolygons > 0:
                for polyObjData in objPolyBlock.obj:
                    if polyObjData.type == 1:
                        create_object(f"track_{i:04}_poly_{index:02}", PolygonType.OBJECT, vertex_buffer, polyObjData, reference_point=center)
                        index += 1
                        
        pass                               
        #break
    
    index = 0
    for xobjBlock in nfs_track.xobj:
        for xobjData in xobjBlock.obj:
            xobj_name = f"xobj_{index:04}_{xobjData.type}"
            loc = xobjData.get_position()
            obj = create_object(
                xobj_name, 
                PolygonType.EXTRAOBJECT, 
                xobjData.vertices_to_buffer(), 
                xobjData, 
                origin=(loc.x, loc.y, loc.z)
            )
            
            if xobjData.type == 3:
                track_verts = [anim.point for anim in xobjData.animData]
                
            index += 1
    
    pass

