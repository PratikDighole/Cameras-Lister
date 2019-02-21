# ##### BEGIN GPL LICENSE BLOCK #####
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

bl_info = {
    "name": "Cameras Lister",
    "author": "Ryxx",
    "blender": (2, 80, 0),
    "description": "Lists all cameras from the scene and allows to easily set the view to a particular one.",
    "location": "Camera Lister Panel shortcut: Alt + C",
    "support": "COMMUNITY",
    "category": "Camera"
}

import bpy
from bpy.types import Operator, Menu, Panel, AddonPreferences

#--------------------------------------------------------------------------------------
# F U N C T I O N A L I T I E S
#--------------------------------------------------------------------------------------

# CAMERA VIEW ON
class CameraViewOn(Operator):
    bl_idname = 'cameras.camera_view_on'
    bl_label = 'Camera View On'
    bl_description = "Camera View On"
    bl_options = {'UNDO'}

    def execute(self,context):
        context.area.spaces[0].region_3d.view_perspective='CAMERA'

        return{'FINISHED'}

# CAMERA VIEW OFF
class CameraViewOff(Operator):
    bl_idname = 'cameras.camera_view_off'
    bl_label = 'Camera View Off'
    bl_description = "Camera View Off"
    bl_options = {'UNDO'}
    
    def execute(self,context):
        context.area.spaces[0].region_3d.view_perspective='PERSP'

        return{'FINISHED'}

# VIEW FROM SELECTED CAMERA
class ViewFromSelectedCamera(Operator):
    bl_idname = 'cameras.view_from_selected'
    bl_label = 'View From Selected'
    bl_description = "Switch to view from selected camera"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.object:
            ob = context.object
            if ob.type == 'CAMERA':
                bpy.ops.view3d.object_as_camera()

        return{'FINISHED'}

# ALIGN SELECTED CAMERA TO VIEW
class AlignSelectedCameraToView(Operator):
    bl_idname = 'cameras.align_selected_to_view'
    bl_label = 'New Camera From View'
    bl_description = "Create a new camera from view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.object:
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
                return {'FINISHED'}
            else:
                ob = context.object
                if ob.type == 'CAMERA':
                    context = bpy.context
                    scene = context.scene
                    currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
                    scene.camera = currentCameraObj
                    bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# NEW CAMERA FROM VIEW
class NewCameraFromView(Operator):
    bl_idname = 'cameras.new_from_view'
    bl_label = 'New Camera From View'
    bl_description = "Create a new camera from view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective='PERSP'
        bpy.ops.object.camera_add()
        context = bpy.context
        scene = context.scene
        currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
        scene.camera = currentCameraObj
        bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# SORTING CAMERAS OPTIONS
sorting_cameras_options = [
        ("alphabetically", "Alphabetically", ""),
        ("by_collections", "By Collections", "")]

bpy.types.Scene.sort_cameras = bpy.props.EnumProperty(
    items=sorting_cameras_options,
    description="Sort cameras",
    default= "alphabetically")

# SET CAMERA VIEW
class SetCameraView(Operator):
    bl_idname = 'cameras.set_view'
    bl_label = 'Set Camera View'
    bl_description = "Set View to this Camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        bpy.ops.cameras.select(camera=self.camera)
        bpy.ops.view3d.object_as_camera()

        return{'FINISHED'}

# Common Draw()
def common_draw(self, context):
    def coll_rec(coll, clist):
        if coll.children:
            for child in coll.children:
                coll_rec(child, clist)
        cams=[cam.name for cam in coll.objects if cam.type=='CAMERA']
        if cams:
            cams.sort(key=str.lower)
            clist.append((coll.name, cams))
    
    layout = self.layout

    box = layout.column(align=True)
    box.label(text="CAMERA INTERACTIVITY", icon="DISCLOSURE_TRI_RIGHT")
    row = box.row(align = False)
    box.separator()
    row.operator("cameras.camera_view_on", text="Camera View On", icon="VIEW_CAMERA")
    row.operator("cameras.camera_view_off", text="Camera View Off", icon="CAMERA_DATA")
    box.operator("cameras.view_from_selected", text="View from Selected", icon="TRIA_RIGHT")
    box.operator("cameras.align_selected_to_view", text="Align Selected to View", icon="TRIA_RIGHT")
    box.operator("cameras.new_from_view", text="New Camera from View", icon="TRIA_RIGHT")
    
    box.separator()
    box.label(text="SCENE CAMERAS LIST", icon="DISCLOSURE_TRI_RIGHT")
    row = box.row(align=True)
    row.prop(context.scene, "sort_cameras", text=" ", expand=True)
    box.separator()
    boxframe = box.box()
    boxframecolumn = boxframe.column()
    sort_option = context.scene.sort_cameras
    if sort_option == sorting_cameras_options[0][0]:
        cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA']
        cam_list.sort(key=str.lower)
        for cam in cam_list:
            row = boxframecolumn.row(align=True)
            row.operator("cameras.set_view", text=cam).camera=cam
            row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam
            row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam
    elif sort_option == sorting_cameras_options[1][0]:
        collcamlist=[]
        master_coll = context.scene.collection
        coll_rec(master_coll, collcamlist)
        collcamlist.sort()
        for coll in collcamlist:
            boxframecolumn.label(text=coll[0])
            for cam in coll[1]:
                row = boxframecolumn.row(align=True)
                row.operator("cameras.set_view", text=cam).camera=cam
                row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam
                row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam


# SELECT CAMERA
class SelectCamera(Operator):
    bl_idname = 'cameras.select'
    bl_label = 'Select Camera'
    bl_description = "Select camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        if context.object:
            if context.object.select_get():
                context.object.select_set(state=False)
                cam=bpy.data.objects[self.camera]
                cam.select_set(state=True)
                context.view_layer.objects.active = cam
                context.scene.camera=cam

        return{'FINISHED'}

# DELETE CAMERA
class DeleteCamera(Operator):
    bl_idname = 'cameras.delete'
    bl_label = 'Delete Camera'
    bl_description = "Delete camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        cam=bpy.data.objects[self.camera]
        bpy.data.objects.remove(cam)
        
        return{'FINISHED'}

#--------------------------------------------------------------------------------------
# P A N E L
#--------------------------------------------------------------------------------------

# CAMERAS LISTER
class CamerasLister(Operator):
    bl_label = "Cameras Lister"
    bl_idname = "cameras.lister"

    def draw(self, context):
        common_draw(self, context)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def execute(self, context):
        self.report({'INFO'}, self.my_enum)
        return {'FINISHED'}

# OPTIONAL PANEL
class VIEW3D_PT_cameraslister(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cameras"
    bl_label = "Cameras Lister"
    
    def draw(self, context):
        common_draw(self, context)
    
class CamerasListerPreferences(AddonPreferences):
    bl_idname = __name__

    def sp_toggle(self, context):
        if self.add_side_panel:
            bpy.utils.register_class(VIEW3D_PT_cameraslister)
        else:
            if hasattr(bpy.types, 'VIEW3D_PT_cameraslister'):
                bpy.utils.unregister_class

    add_side_panel: bpy.props.BoolProperty(name="side_panel", default=False, update=sp_toggle)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Custom settings:")
        split=layout.split()
        split.label(text="Add CamerasLister to Side Panel:")
        split.prop(self, "add_side_panel")

#--------------------------------------------------------------------------------------
# R E G I S T R Y
#--------------------------------------------------------------------------------------

classes = (
    CameraViewOn,
    CameraViewOff,
    ViewFromSelectedCamera,
    AlignSelectedCameraToView,
    NewCameraFromView,
    SetCameraView,
    SelectCamera,
    DeleteCamera,
    CamerasLister,
    CamerasListerPreferences
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    wm = bpy.context.window_manager

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('cameras.lister', 'C', 'PRESS', alt=True)
    kmi.active = True

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    if hasattr(bpy.types, 'VIEW3D_PT_cameraslister'):
        bpy.utils.unregister_class(VIEW3D_PT_cameraslister)
    

    addon_keymaps = []
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymaps.clear()

if __name__ == "__main__":
    register()
