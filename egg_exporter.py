import os
import sys
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
#logger.disabled = True

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

path = os.getcwd()
logger.info(path)

import bpy

import math


def write(letter_list):
    with open("absolute path", mode="w", encoding="UTF-8") as f:
        for letter in letter_list:
            f.write(letter)



class RenderFirst():
    def __init__(self):
        self.letter = ""

    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter):
        self.letter += letter

    def render(self):
        letter = ""
        self.coordinate()
        self.material()
        self.texture()

    def coordinate(self):
        letter = ""
        letter += "<CoordinateSystem> { Z-up }"
        letter += "\n"
        self.save_letter(letter)

    def material(self):
        letter = ""

        self.all_materials = []
        for obj in selected_objects:
            if obj.type != "MESH":
                continue
            for mat_slot in obj.material_slots:
                material = mat_slot.material
                if material:
                    if material not in self.all_materials:
                        self.all_materials.append(material)

        for material in self.all_materials:
            letter += "<Material>"
            letter += f" {material.name} "
            letter += "{"
            letter += "\n"

            lst = ["diffr", "diffg", "diffb", "diffa"]
            for i in range(4):
                letter = self.render_indent(letter, 1)
                letter += "<Scalar>"
                letter += f" {lst[i]} "
                letter += "{ 1.0 }"
                letter += "\n"
            
            letter = self.render_indent(letter, 1)
            letter += "<Scalar> local { 1 }"
            letter += "\n"

            letter += "}"
            letter += "\n"
        self.save_letter(letter)

    def texture(self):
        all_textures = []
        for material in self.all_materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE":
                        if node.image.name not in all_textures:
                            all_textures.append(node.image.name)
        letter = ""
        for texture_name in all_textures:
            letter += "<Texture>"
            letter += f" {texture_name} "
            letter += "{"
            letter += "\n"
            letter = self.render_indent(letter, 1)
            letter += f"./tex/{texture_name}"
            letter += "\n"

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> format { rgba }"
            letter += "\n"

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> envtype { modulate }"
            letter += "\n"       

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> uv-name { UVMap }"
            letter += "\n"       

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> minfilter { linear_mipmap_linear }"
            letter += "\n"

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> magfilter { linear }"
            letter += "\n"

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> wrapu { repeat }"
            letter += "\n"

            letter = self.render_indent(letter, 1)
            letter += "<Scalar> wrapv { repeat }"
            letter += "\n"

            letter += "}"
            letter += "\n"
        
        self.save_letter(letter)



class RenderMaster():
    def __init__(self):
        self.master_letter = ""
        self.render_armature_obj = RenderArmature()

        #self.is_no_texture = False

    def pack_all(self):
        self.master_letter += self.render_armature_obj.letter_start
        self.master_letter += self.render_armature_obj.letter_joint
        for render_mesh_obj_obj in self.render_mesh_obj_list:
            self.master_letter += render_mesh_obj_obj.master_letter
        self.master_letter += self.render_armature_obj.letter_end

    def render_all(self):
        self.bone_vertex_dict = {}

        self.render_mesh_obj_list = []

        for child in obj_armature.children:
            if child not in selected_objects:
                continue    
            render_mesh_obj_obj = RenderMeshObj(child)
            self.render_mesh_obj_list.append(render_mesh_obj_obj)
            self.render_mesh_obj(child, render_mesh_obj_obj, False)
        self.render_armature_obj.render_all(self.bone_vertex_dict)
        self.pack_all()

    def render_mesh_obj(self, obj, render_mesh_obj_obj, is_no_texture):
        if obj.data.shape_keys:
            shape_key_names = obj.data.shape_keys.key_blocks.keys()
        else:
            shape_key_names = []

        master_indent = 1

        uv_layer = obj.data.uv_layers[0]

        self.my_vertex_data_list = []

        v_idx_egg = 0
        for polygon in obj.data.polygons:
            polygon_egg_idx_list = []

            for loop_idx in polygon.loop_indices:
                loop = obj.data.loops[loop_idx]
                vertex_idx = loop.vertex_index
                #loop_idx = loop.index

                vertex = obj.data.vertices[vertex_idx]

                if is_no_texture:
                    uv_pos = (0, 0)
                else:
                    uv = uv_layer.data[loop_idx].uv
                    uv_pos = (round(uv.x, 4), round(uv.y, 4))

                for my_v_data in reversed(self.my_vertex_data_list): #後ろからやった方が速いはず。
                    if my_v_data.idx == vertex_idx:
                        for egg_v_data in my_v_data.egg_vertex_list:
                            if uv_pos == egg_v_data.uv_pos: #同じuv座標が入っていたら　書き込まない。
                                polygon_egg_idx_list.append(egg_v_data.idx)
                                break
                        else:
                            egg_v_data = MyVertexDataEgg(v_idx_egg, uv_pos)
                            my_v_data.egg_vertex_list.append(egg_v_data) #uv_posがappend されたら　v_idx_eggも+1
                            polygon_egg_idx_list.append(egg_v_data.idx)
                            render_mesh_obj_obj.vert_obj.render_single(egg_v_data, vertex, shape_key_names, master_indent)
                            v_idx_egg += 1
                        break
                else:
                    my_v_data = MyVertexData(vertex_idx, vertex)
                    egg_v_data = MyVertexDataEgg(v_idx_egg, uv_pos)
                    my_v_data.egg_vertex_list.append(egg_v_data)
                    self.my_vertex_data_list.append(my_v_data)
                    polygon_egg_idx_list.append(egg_v_data.idx)
                    render_mesh_obj_obj.vert_obj.render_single(egg_v_data, vertex, shape_key_names, master_indent)
                    v_idx_egg += 1

            render_mesh_obj_obj.poly_obj.render_single(polygon, polygon_egg_idx_list)

        render_mesh_obj_obj.finish()

        self.bone_vertex_dict[obj] = self.my_vertex_data_list.copy()
        

        
class RenderArmature():
    def __init__(self):
        self.letter_start = ""
        self.letter_joint = ""
        self.letter_end = ""

    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter, name):
        setattr(self, name, getattr(self, name) + letter)

    def render_all(self, bone_vertex_dict):
        self.render_start()
        self.render_joint(bone_vertex_dict)
        self.render_end()

    def render_start(self):
        name = obj_armature.name
        letter = ""
        letter = self.render_indent(letter, 0)

        letter += "<Group>"
        letter += f" {name} "
        letter += "{"
        letter += "\n"

        letter = self.render_indent(letter, 1)
        letter += "<Dart> { 1 }"
        letter += "\n"

        self.save_letter(letter, "letter_start")

    def render_end(self):
        self.letter = ""
        letter = ""
        letter = self.render_indent(letter, 0)
        letter += "}"
        letter += "\n"
        self.save_letter(letter, "letter_end")

    def render_joint(self, bone_vertex_dict):
        self.rendered_bones = []
        master_bone = obj_armature.data.bones["waist"]
        self.single_bone(master_bone, 1, bone_vertex_dict)
        print(f"{self.rendered_bones}")

    def single_bone(self, bone, indent_num, bone_vertex_dict):
        print(f"{bone.name}")
        if "control" in bone.name:
            return

        self.render_single_bone_first(bone, indent_num)
        for child in obj_armature.children:
            if child not in selected_objects:
                continue
            vertex_group = child.vertex_groups.get(bone.name)
            if vertex_group is None:
                continue
            self.render_single_bone_vertex_data(bone, indent_num, child, bone_vertex_dict)

        self.rendered_bones.append(bone.name)
        for child_bone in bone.children:
            self.single_bone(child_bone, indent_num + 1, bone_vertex_dict)

        #childがなくなったらboneの括弧を閉じる
        letter = ""
        letter = self.render_indent(letter, indent_num)
        letter += "}"
        letter += "\n"
        letter += "\n"
        self.save_letter(letter, "letter_joint")

    def render_single_bone_first(self, bone, indent_num):
        letter = ""
        letter = self.render_indent(letter, indent_num)
        letter += "<Joint>"
        letter += f" {bone.name} "
        letter += "{"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 1)
        letter += "<Transform>"
        letter += " {"
        letter += "\n"


        if bone.parent:
            mat = bone.parent.matrix_local.inverted() @ bone.matrix_local
        else:
            mat = bone.matrix_local
        scale = mat.to_scale()
        rot = mat.to_euler()
        pos = mat.to_translation()

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<Scale>"
        letter += " { "
        letter += f"{scale.x} {scale.y} {scale.z}"
        letter += " }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<RotX>"
        letter += " { "
        letter += f"{math.degrees(rot.x)}"
        letter += " }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<RotY>"
        letter += " { "
        letter += f"{math.degrees(rot.y)}"
        letter += " }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<RotZ>"
        letter += " { "
        letter += f"{math.degrees(rot.z)}"
        letter += " }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<Translate>"
        letter += " { "
        letter += f"{pos[0]} {pos[1]} {pos[2]}"
        letter += " }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 1)
        letter += "}"
        letter += "\n"

        self.save_letter(letter, "letter_joint")

    def render_single_bone_vertex_data(self, bone, indent_num, obj_mesh, bone_vertex_dict):
        vertex_group = obj_mesh.vertex_groups.get(bone.name)

        letter = ""

        w_lst = []
        v_lst = []

        obj_vertex_data_list = bone_vertex_dict[obj_mesh]
        for my_v_data in obj_vertex_data_list:
            for group in my_v_data.vertex_blender.groups:
                if group.group == vertex_group.index:
                    idx_list = []
                    for my_egg_v_data in my_v_data.egg_vertex_list:
                        idx_list.append(my_egg_v_data.idx)
                    #idx = my_v_data.idx
                    w_2 = round(group.weight, 3)
                    for i, w in enumerate(w_lst):
                        if w == w_2:
                            v_lst[i].extend(idx_list)
                            break
                    else:
                        w_lst.append(w_2)
                        v_lst.append([])
                        v_lst[-1].extend(idx_list)

        length = len(w_lst)
        for i in range(length):
            letter = self.render_indent(letter, indent_num + 1)
            letter += "<VertexRef>"
            letter += " {"
            letter += "\n"
            
            letter = self.render_indent(letter, indent_num + 2)
            v_s = v_lst[i]
            for v_idx in v_s:
                letter += f"{v_idx} "
            letter += "\n"

            w = w_lst[i]
            letter = self.render_indent(letter, indent_num + 2)
            letter += "<Scalar> membership { "
            letter += f"{w}"
            letter += " } "
        
            letter += "<Ref>"
            letter += " { "
            letter += f'"{obj_mesh.name}"'
            letter += " }"
            letter += "\n"

            letter = self.render_indent(letter, indent_num + 1)
            letter += "}"
            letter += "\n"

        self.save_letter(letter, "letter_joint")

class RenderMeshObj():
    def __init__(self, obj):
        self.master_letter = ""
        self.letter_start = ""
        self.letter_end = ""
        self.obj = obj

        self.vert_obj = RenderVertex(obj)
        self.poly_obj = RenderPolygon(obj)

    def reset(self):
        self.master_letter = ""
        self.letter_start = ""
        self.letter_end = ""

    def finish(self):
        self.render_start()
        self.render_end()
        self.vert_obj.render_start()
        self.vert_obj.render_end()
        self.pack()

    def pack(self):
        self.master_letter += self.letter_start
        self.vert_obj.pack()
        self.master_letter += self.vert_obj.master_letter
        self.master_letter += self.poly_obj.letter
        self.master_letter += self.letter_end


    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter, name):
        setattr(self, name, getattr(self, name) + letter)

    def render_start(self):
        master_indent = 1
        letter = ""
        letter = self.render_indent(letter, master_indent)
        letter += f"<Group> {self.obj.name}"
        letter += " {"
        letter += "\n"
        if self.obj.data.shape_keys:
            letter = self.render_indent(letter, master_indent + 1)
            letter += "<Dart> { 1 }"
            letter += "\n"
        self.save_letter(letter, "letter_start")

    def render_end(self):
        letter = ""
        letter = self.render_indent(letter, 1)
        letter += "}"
        letter += "\n"
        self.save_letter(letter, "letter_end")


class RenderVertex():
    def __init__(self, object):
        self.master_letter = ""
        self.letter_pool_start = ""
        self.letter_single_vertices = ""
        self.letter_pool_end = ""
        self.obj = object

    def reset(self):
        self.master_letter = ""
        self.letter_pool_start = ""
        self.letter_single_vertices = ""
        self.letter_pool_end = ""

    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter, name):
        setattr(self, name, getattr(self, name) + letter)

    def pack(self):
        self.master_letter = ""

        self.master_letter += self.letter_pool_start
        self.master_letter += self.letter_single_vertices
        self.master_letter += self.letter_pool_end

    def render_start(self):
        master_indent = 1
        letter = ""
        letter = self.render_indent(letter, master_indent + 1)
        letter += f"<VertexPool> {self.obj.name}"
        letter += " {"
        letter += "\n"
        self.save_letter(letter, "letter_pool_start")

    def render_end(self):
        master_indent = 1
        letter = ""
        letter = self.render_indent(letter, master_indent + 1)
        letter += "}"
        letter += "\n"
        self.save_letter(letter, "letter_pool_end")


    def render_single(self, egg_v_data, vertex, shape_key_names, master_indent):
        def render_shape_key():
            letter = ""
            letter = self.render_indent(letter, master_indent + 3)
            letter += "<Dxyz>"
            letter += f" {key_name} "
            letter += "{ "

            pos = self.obj.data.shape_keys.key_blocks[key_name].data[vertex.index].co
            diff = pos - vertex.co #シェイプキーは差分
            letter += f"{round(diff[0], 4)} {round(diff[1], 4)} {round(diff[2], 4)}"
            #letter += f"{round(pos[0], 4)} {round(pos[1], 4)} {round(pos[2], 4)}"
            
            letter += " }"
            letter += "\n"
            self.save_letter(letter, "letter_single_vertices")


        letter = ""
        letter = self.render_indent(letter, master_indent + 2)
        letter += "<Vertex>"

        letter += f" {egg_v_data.idx} "
        letter += "{"
        letter += "\n"

        letter = self.render_indent(letter, master_indent + 3)
        pos = vertex.co
        letter += f"{round(pos[0], 4)} {round(pos[1], 4)} {round(pos[2], 4)}"
        letter += "\n"
        self.save_letter(letter, "letter_single_vertices")

        for key_name in shape_key_names:
            if key_name == "Basis":
                continue
            render_shape_key()
        
        letter = ""
        letter = self.render_indent(letter, master_indent + 3)
        letter += "<Normal>"
        letter += " { "
        normal = vertex.normal
        letter += f"{round(normal[0], 4)} {round(normal[1], 4)} {round(normal[2], 4)}"
        letter += " } "
        letter += "\n"

        letter = self.render_indent(letter, master_indent + 3)
        letter += "<UV> UVMap"
        letter += " { "
        letter += f"{egg_v_data.uv_pos[0]} {egg_v_data.uv_pos[1]}"
        letter += " } "
        letter += "\n"
        
        letter = self.render_indent(letter, master_indent + 2)
        letter += "}"
        letter += "\n"

        self.save_letter(letter, "letter_single_vertices")





        

class RenderPolygon():    
    def __init__(self, object):
        self.letter = ""
        self.obj = object

    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter):
        self.letter += letter

    def render_single(self, polygon, polygon_egg_v_idx_list):
        #self.letter = ""
        letter = ""
        master_indent = 2
        materials = self.obj.material_slots

        letter = self.render_indent(letter, master_indent)
        letter += "<Polygon>"
        letter += " { "
        letter += "\n"

        material = materials[polygon.material_index].material

        if material.use_nodes: #もしそのpolygonにtexureがあるのなら、textureを追加
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    letter = self.render_indent(letter, master_indent + 1)
                    letter += "<TRef>"
                    letter += " { "
                    letter += node.image.name
                    letter += " } "
                    letter += "\n"

        letter = self.render_indent(letter, master_indent + 1)
        letter += "<MRef>"
        letter += " { "
        letter += material.name
        letter += " } "
        letter += "\n"

        letter = self.render_indent(letter, master_indent + 1)
        letter += "<VertexRef>"
        letter += " { "

        v_let = ""
        for v_idx in polygon_egg_v_idx_list:
            v_let += f"{v_idx} "        
        letter += v_let

        letter += "<Ref>"
        letter += " { "
        letter += self.obj.name
        letter += " } "
        letter += "}"
        letter += "\n"

        letter = self.render_indent(letter, master_indent)
        letter += "}"
        letter += "\n"

        self.save_letter(letter)


class MyPolygonData():
    def __init__(self):
        self.idx_egg = idx_egg
        
        self.vertices = []



class MyVertexData():
    def __init__(self, idx, v_blender):
        self.idx = idx
        self.vertex_blender = v_blender

        self.egg_vertex_list = []

class MyVertexDataEgg():
    def __init__(self, idx, uv_pos):
        self.idx = idx
        self.uv_pos = uv_pos




selected_objects = bpy.context.selected_objects

obj_armature = bpy.context.active_object

letter_list = []

render_first = RenderFirst()
render_first.render()
letter_list.append(render_first.letter)

render_master = RenderMaster()
render_master.render_all()
letter_list.append(render_master.master_letter)

write(letter_list)
