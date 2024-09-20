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


class RenderMaster():
    def __init__(self):
        self.letter_master = ""
        self.letter_start = ""

    def pack(self):
        pass

    def render_all(self):
        self.letter_start += "<CoordinateSystem> { Z-up }"
        self.letter_start += "\n"


class RenderArmatureAnim():
    def __init__(self, obj, action_name):
        self.obj = obj
        self.action_name = action_name
        self.letter = ""

    def render_indent(self, letter, indent_num):
        for i in range(indent_num):
            letter += "  "
        return letter

    def save_letter(self, letter):
        self.letter += letter

    def anim_name(self):
        #for track in obj.animation_data.nla_traks:
        #    if track.name == "track_name":
        #        track.mute = False
        #    else:
        #        track.mute = True
        #for action in bpy.data.actions: 
        #    if action.name == my_action_name:
        action = bpy.data.actions[self.action_name]
        self.obj.animation_data.action = action
        self.frame_start = action.frame_range[0]
        self.frame_end = action.frame_range[1]

    def render_start(self):
        letter = ""
        letter += "<Table> {"
        letter += "\n"

        letter = self.render_indent(letter, 1)
        letter += "<Bundle> armature {"
        letter += "\n"

        letter = self.render_indent(letter, 2)
        letter += '<Table> "<skeleton>" {'
        letter += "\n"

        self.save_letter(letter)

    def render_end(self):
        letter = ""
        letter = self.render_indent(letter, 2)
        letter += "}" #table skeleton を閉じる
        letter += "\n"

        letter = self.render_indent(letter, 1)
        letter += "}" #bundle armature を閉じる   
        letter += "\n"

        letter = self.render_indent(letter, 0)
        letter += "}" #table を閉じる
        letter += "\n"

        self.save_letter(letter)

    def render_joint(self):
        master_bone = self.obj.data.bones["waist"]
        self.single_bone(master_bone, 3)

    def single_bone(self, bone, indent_num):
        print(f"{bone.name}")
        if "control" in bone.name:
            return
        self.render_single_bone_anim(bone, indent_num)
        for child_bone in bone.children:
            self.single_bone(child_bone, indent_num + 1)

        #childがなくなったらboneの括弧を閉じる
        letter = ""
        letter = self.render_indent(letter, indent_num)
        letter += "}"
        letter += "\n"
        letter += "\n"
        self.save_letter(letter)

    def render_single_bone_anim(self, bone, indent_num):
        letter = ""
        letter = self.render_indent(letter, indent_num)
        letter += "<Table>"
        letter += f" {bone.name} "
        letter += " { "
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 1)
        letter += "<Xfm$Anim> xform {"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<Scalar> fps { 24 }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<Scalar> order { sprht }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<Scalar> contents { ijkprhxyz }"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 2)
        letter += "<V> {"
        letter += "\n"


        for frame_number in range(int(self.frame_start), int(self.frame_end)):
            bpy.context.scene.frame_set(frame_number)
            pose_bone = self.obj.pose.bones[bone.name]
            if pose_bone.parent:
                mat = pose_bone.parent.matrix.inverted() @ pose_bone.matrix
            else:
                mat = self.obj.matrix_world @ pose_bone.matrix
            pos = mat.to_translation()
            rot = mat.to_euler()
            scale = mat.to_scale()
            #mat = bone.matrix_local
            #mat_w = self.obj.convert_space(pose_bone=pose_bone, matrix=pose_bone.matrix, from_space="POSE", to_space="WORLD")
            #pos = mat_w.to_translation()
            #pos = pose_bone.head
            #pos = (0, 0, 0)
            #rot = (0, 0, 0)
            #scale = (1, 1, 1)
            #pos = pose_bone.location
            #rot = pose_bone.rotation_euler
            #scale = pose_bone.scale
            #rot = mat_w.to_euler() #radians
            #scale = mat_w.to_scale()


            letter = self.render_indent(letter, indent_num + 3)
            letter += f"{round(scale[0], 4)} {round(scale[1], 4)} {round(scale[2], 4)}"
            letter += " "
            letter += f"{round(math.degrees(rot[0]), 4)} {round(math.degrees(rot[1]), 4)} {round(math.degrees(rot[2]), 4)}"
            letter += " "
            letter += f"{round(pos[0], 4)} {round(pos[1], 4)} {round(pos[2], 4)}"
            letter += "\n"

        letter = self.render_indent(letter, indent_num + 2) 
        letter += "}"
        letter += "\n"

        letter = self.render_indent(letter, indent_num + 1)
        letter += "}"
        letter += "\n"


        self.save_letter(letter)


render_master = RenderMaster()
render_master.render_all()
letter_list = []
letter_list.append(render_master.letter_start)

obj_armature = bpy.context.active_object
render_armature_anim = RenderArmatureAnim(obj_armature, "action_name")
render_armature_anim.anim_name()
render_armature_anim.render_start()
render_armature_anim.render_joint()
render_armature_anim.render_end()

letter_list.append(render_armature_anim.letter)

write(letter_list)
