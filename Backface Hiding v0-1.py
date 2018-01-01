# ##### BEGIN GPL LICENSE BLOCK #####
#
# Backface Hiding hides backfacing or non-visible geometry in Edit mode.
# Copyright (C) 2015 Eric Gentry
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Backface hiding",
	"description": "button to Hide backfacing geometry in Edit mode",
	"author": "Caetano Veyssières (ChameleonScales)",
	"version": (0, 1),
	"blender": (2, 79, 0),
	"location": "3D View(s) -> Properties Region -> Mesh Display",
	"warning": "Using the button will deselect vertices, edges and faces. Also, it only updates every time you click on the button, not in real time",
    "wiki_url": "https://github.com/ChameleonScales/Backface-Hiding",
    "tracker_url": "https://github.com/ChameleonScales/Backface-Hiding/issues",
	"category": "3D View",
	}

import bpy
from mathutils import Vector

handle = []
bm_old = [None]

class HideBackfacingOperator(bpy.types.Operator):
	bl_idname = "object.hide_backfacing"
	bl_label = "Hide Backfacing"
	bl_description = "Hide backfacing geometry"
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.reveal()
		
		#Use user view for plane rotation
		viewMatrix=context.region_data.view_matrix.transposed()
		bpy.ops.mesh.primitive_plane_add()
		bpy.ops.object.mode_set(mode='OBJECT')
		for vert in bpy.context.object.data.vertices:
			if vert.select:
				planeVector = Vector((vert.co.x,vert.co.y,vert.co.z,1))
				movedVertices= viewMatrix * planeVector
				vert.co = movedVertices[0:3]
		
		#Make the plane active (for later deletion) :
		for face in bpy.context.object.data.polygons:
			if face.select:
				bpy.context.object.data.polygons.active = face.index
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_similar(type='NORMAL', threshold=0.5)
		bpy.ops.mesh.hide(unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		#Select the plane and delete it
		bpy.ops.object.mode_set(mode='OBJECT')
		for face in bpy.context.object.data.polygons:
			if bpy.context.object.data.polygons.active==face.index:
				face.select=True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='FACE')
		
		return {'FINISHED'}

class HideNonVisibleOperator(bpy.types.Operator):
	bl_idname = "object.hide_non_visible"
	bl_label = "Hide non visible"
	bl_description = "Hide non visible geometry"
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		#bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.reveal()
		bpy.context.space_data.use_occlude_geometry = True
		bpy.ops.view3d.select_border(gesture_mode=3, xmin=0, xmax=bpy.context.area.width, ymin=0, ymax=bpy.context.area.height, extend=False)
		bpy.ops.mesh.hide(unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		return {'FINISHED'}

def displayBackfaceHidingPanel(self, context):

	if context.active_object and context.active_object.type == 'MESH':
		box = self.layout.box()
		box.operator("object.hide_backfacing", text="Hide backfacing", icon='VISIBLE_IPO_OFF')
		box.operator("object.hide_non_visible", text="Hide non visible", icon='ORTHO')
	

def register():
	bpy.utils.register_module(__name__)

	bpy.types.VIEW3D_PT_view3d_meshdisplay.append(displayBackfaceHidingPanel)

	

def unregister():
	bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(displayBackfaceHidingPanel)
	del bpy.types.Object.backface_hiding
	if handle:
		bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
		handle[:] = []
	bpy.utils.unregister_module(__name__)
	

if __name__ == "__main__":
	register()