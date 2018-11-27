# ##### BEGIN GPL LICENSE BLOCK #####
#
#  FPS setup, a Blender addon
#  (c) 2016 Tim Crellin (Thatimst3r)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {"name": "FPS setup", "category": "Game Engine", "author": "Tim Crellin (Thatimst3r) contributions by google and coffee", "blender": (2,77,0), "location": "View3D > UI toolbar (n)", "description":"Adds a simple FPS setup at cursor location","warning": "","wiki_url":"", "tracker_url": "", "version":(1,0)}

import bpy
import math
import mathutils

def setup():
    scene = bpy.context.scene

    #----body----#
    #add the main body
    bpy.types.MESH_OT_primitive_cylinder_add.vertices = bpy.props.IntProperty(name="Vertices",default=12)
    bpy.ops.mesh.primitive_cylinder_add()
    body = bpy.context.object
    body.name = 'player_body'
    body.hide_render = True
    body.game.use_actor = True
    body.game.physics_type = 'DYNAMIC'
    body.game.use_collision_bounds = True
    body.game.collision_bounds_type = 'CYLINDER'
    body.scale = ((1, 1, 2))

    set_pos = bpy.context.scene.cursor_location + mathutils.Vector([0,0,2])
    body.location = set_pos
    #apply the scale
    bpy.ops.object.transform_apply(scale = True)

    controls = [('W',(1,0.1)),('S',(1,-0.1)),('A',(0,-0.1)),('D',(0,0.1)),('LEFT_SHIFT',(1,0.2)),('SPACE',(2,8))]

    for key in controls:
        bpy.ops.logic.sensor_add(type="KEYBOARD",name=key[0],object=body.name)
        bpy.ops.logic.controller_add(type="LOGIC_AND",object=body.name)
        bpy.ops.logic.actuator_add(type="MOTION",name=key[0]+"_move",object=body.name)
        
        sensor = body.game.sensors[-1]
        control = body.game.controllers[-1]
        actuator=body.game.actuators[-1]

        sensor.key = key[0]
        sensor.use_pulse_true_level = True
        actuator.offset_location[key[1][0]] = key[1][1]
        
        sensor.link(control)
        actuator.link(control)
        
        control.show_expanded = False
        sensor.show_expanded = False
        actuator.show_expanded = False
        
        if key[0] == "LEFT_SHIFT":
            body.game.sensors[0].link(control)
        elif key[0] == 'SPACE':
            bpy.ops.logic.sensor_add(type="COLLISION",name='jump',object=body.name)
            body.game.sensors[-1].link(control)
            actuator.mode = "OBJECT_SERVO"
            actuator.linear_velocity[key[1][0]] = key[1][1]
            actuator.use_servo_limit_z = True
            actuator.force_max_z = 200
            actuator.force_min_z = -200

    #mouse horizontal look        
    bpy.ops.logic.sensor_add(type="MOUSE",name='mouse',object=body.name)
    bpy.ops.logic.controller_add(type="LOGIC_AND",object=body.name)
    bpy.ops.logic.actuator_add(type="MOUSE",name="look_horiz",object=body.name)

    body.game.sensors[-1].mouse_event = "MOVEMENT"
    body.game.actuators[-1].mode = "LOOK"
    body.game.actuators[-1].sensitivity_x = 1.6
    body.game.actuators[-1].use_axis_y = False
    body.game.actuators[-1].use_axis_y = False

    body.game.sensors[-1].show_expanded = False
    body.game.controllers[-1].show_expanded = False
    body.game.actuators[-1].show_expanded = False
    body.game.sensors[-1].link(body.game.controllers[-1])
    body.game.actuators[-1].link(body.game.controllers[-1])
        

    #----head----#
    parent_to = body.name
    bpy.ops.object.add(type="EMPTY")
    head= bpy.context.object
    head.name = 'player_head'
    head.game.physics_type = 'NO_COLLISION'
    head.empty_draw_type = 'SPHERE'
    head.location = ((0,0,1))
    head.parent = bpy.data.objects[parent_to]
    head.scale = ((0.6,0.6,0.6))
    bpy.ops.object.transform_apply(scale = True)
    #### add logic ####
    bpy.ops.logic.sensor_add(type="MOUSE",name="movement",object=head.name)
    bpy.ops.logic.controller_add(type="LOGIC_AND",object=head.name)
    bpy.ops.logic.actuator_add(type="MOUSE",name='mouse_look',object=head.name)

    ### modify logic ###
    sensor = head.game.sensors[-1]
    control = head.game.controllers[-1]
    actuator=head.game.actuators[-1]

    sensor.mouse_event = "MOVEMENT"
    actuator.mode = "LOOK"
    actuator.use_axis_x = False
    actuator.sensitivity_y = 1.6

    sensor.link(control)
    sensor.show_expanded = False
    control.show_expanded = False
    actuator.link(control)
    actuator.show_expanded = False

    #----camera-----#
    #player camera initial settings
    parent_cam = head.name
    bpy.ops.object.camera_add(location=(0.0,0.0,0.0),rotation=(math.radians(90),0,0))
    cam = bpy.context.object
    cam.name = 'player_camera'
    cam.game.physics_type = 'NO_COLLISION'
    cam.parent = bpy.data.objects[parent_cam]
    cam.scale = ((0.5,0.5,0.5))
    #set active+angle
    bpy.context.scene.camera = cam
    bpy.data.cameras[cam.data.name].lens = 25
    
    #set selected object as body
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[body.name]
    body.select = True
    body.draw_type = "WIRE"

def set_cam():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'


class AddFPS(bpy.types.Operator):
    bl_idname = "object.add_fps"
    bl_description = 'Add a simple FPS setup at 3d cursor'
    bl_label = "Add FPS"
    bl_options = {"REGISTER","UNDO"}
    
    def execute(self, context):
        setup()
        self.report({'INFO'}, "New FPS setup added")
        return {"FINISHED"}

class FPSPanel(bpy.types.Panel):
    bl_label = "FPS setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.add_fps",text='Add FPS Setup',icon="OUTLINER_DATA_CAMERA",)
        
        

def register():
    bpy.utils.register_class(FPSPanel)
    bpy.utils.register_class(AddFPS)

def unregister():
    bpy.utils.unregister_class(FPSPanel)
    bpy.utils.unregister_class(AddFPS)

if __name__ == "__main__":
    register()
    