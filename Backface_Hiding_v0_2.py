# ##### BEGIN GPL LICENSE BLOCK #####
#
# Backface Hiding hides backfacing or non-visible geometry in Edit mode.
# Copyright (C) 2018 Caetano VeyssiÃšres
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
	"author": "Caetano VeyssiÃšres (ChameleonScales)",
	"version": (0, 2),
	"blender": (2, 79, 0),
	"location": "3D View(s) -> Properties Region -> Mesh Display",
	"warning": "at the current version, the object's rotation needs to be at (0,0,0) in order for the hiding features to be oriented properly.",
    "wiki_url": "https://github.com/ChameleonScales/Backface-Hiding",
    "tracker_url": "https://github.com/ChameleonScales/Backface-Hiding/issues",
	"category": "3D View",
	}

import bpy
import bmesh
from mathutils import Vector
from bpy.props import BoolProperty
from bpy.types import AddonPreferences, PropertyGroup
#from bpy.types import Menu, Header
import rna_keymap_ui

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

	def execute(self, context) :
		# Store original select mode:
		original_select_mode = bpy.context.tool_settings.mesh_select_mode[0:3]
		# Store original selection :
		bpy.ops.object.mode_set(mode='OBJECT')
		meshData = bpy.context.object.data
		vertex_selection = [v.index for v in meshData.vertices if v.select]
		edge_selection = [e.index for e in meshData.edges if e.select]
		face_selection = [f.index for f in meshData.polygons if f.select]
		
		# Un-hide everything (and go in face selection mode)
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.reveal()
		
		# Add a plane and rotate it to face the view :
		bpy.ops.mesh.primitive_plane_add()
		bpy.ops.object.mode_set(mode='OBJECT')
		viewMatrix=context.region_data.view_matrix.transposed()
		for vert in bpy.context.object.data.vertices:
			if vert.select:
				planeVector = Vector((vert.co.x,vert.co.y,vert.co.z,1))
				movedVertices= viewMatrix * planeVector
				vert.co = movedVertices[0:3]
		
		# Make the plane active (for later deletion) :
		for face in bpy.context.object.data.polygons:
			if face.select:
				bpy.context.object.data.polygons.active = face.index
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_similar(type='NORMAL', threshold=0.5)
		bpy.ops.mesh.hide(unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		
		# Select the plane and delete it
		bpy.ops.object.mode_set(mode='OBJECT')
		for face in bpy.context.object.data.polygons:
			if bpy.context.object.data.polygons.active==face.index:
				face.select=True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='FACE')
		
		# Restore original select mode :
		bpy.context.tool_settings.mesh_select_mode=original_select_mode
		
		# Restore original selection :
		bpy.ops.object.mode_set(mode='OBJECT')
		for vi in vertex_selection:
			meshData.vertices[vi].select = True
		for ei in edge_selection:
			meshData.edges[ei].select = True
		for fi in face_selection:
			meshData.polygons[fi].select = True
		bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}

class HideNonVisibleOperator(bpy.types.Operator):
	bl_idname = "object.hide_non_visible"
	bl_label = "Hide non-visible"
	bl_description = "Hide non-visible geometry"
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		
		# Store original select mode:
		original_select_mode = bpy.context.tool_settings.mesh_select_mode[0:3]
		
		# Store original selection :
		bpy.ops.object.mode_set(mode='OBJECT')
		meshData = bpy.context.object.data
		vertex_selection = [v.index for v in meshData.vertices if v.select]
		edge_selection = [e.index for e in meshData.edges if e.select]
		face_selection = [f.index for f in meshData.polygons if f.select]
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.reveal()
		
		# Store original "Limit selection to visible" :
		original_occlude_mode = bpy.context.space_data.use_occlude_geometry
		
		# Enable "Limit selection to visible" :
		bpy.context.space_data.use_occlude_geometry = True
		
		# Border select geometry with a rectangle that fills the 3DView Area
		bpy.ops.view3d.select_border(gesture_mode=3, xmin=0, xmax=bpy.context.area.width, ymin=0, ymax=bpy.context.area.height, extend=False)
		
		# Hide non-selected geometry
		bpy.ops.mesh.hide(unselected=True)
		
		bpy.ops.mesh.select_all(action='DESELECT')
		
		# Retore original "Limit selection to visible" :
		bpy.context.space_data.use_occlude_geometry = original_occlude_mode
		
		# Restore original select mode :
		bpy.context.tool_settings.mesh_select_mode=original_select_mode
		
		# Restore original selection :
		bpy.ops.object.mode_set(mode='OBJECT')
		for vi in vertex_selection:
			meshData.vertices[vi].select = True
		for ei in edge_selection:
			meshData.edges[ei].select = True
		for fi in face_selection:
			meshData.polygons[fi].select = True
		bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}

# Preferences            
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
    
	use_backface_hiding = BoolProperty(
			name="Use Pie Menu", 
			default=True
			)

def displayBackfaceHidingPanel(self, context):

	if context.active_object and context.active_object.type == 'MESH':
		box = self.layout.box()
		box.operator("object.hide_backfacing", text="Hide backfacing", icon='VISIBLE_IPO_OFF')
		box.operator("object.hide_non_visible", text="Hide non-visible", icon='ORTHO')

		# Hotkey layout :
		if self.use_backface_hiding :
			split = box.split()
			col = split.column()       
			col.label('Setup backface hiding Hotkey')
			col.separator()

			col.label('Setup Hotkey')
			col.separator()
			wm = bpy.context.window_manager
			kc = wm.keyconfigs.user
			km = kc.keymaps['3D View Generic']
			kmi = get_hotkey_entry_item(km, 'object.hide_backfacing', 'object.hide_backfacing')
			if kmi:
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
			else:
				col.label("No hotkey entry found")
				col.operator(SpeedRetopoAddHotkey.bl_idname, text = "Add hotkey entry", icon = 'ZOOMIN')
				
				
				row = box.row(align=True)
				row.label("Save preferences to apply these settings", icon='ERROR')
	
addon_keymaps = [] 
         

def get_hotkey_entry_item(km, kmi_name, kmi_value):
	'''
	returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
	if there are multiple hotkeys!)
	'''
	for i, km_item in enumerate(km.keymap_items):
		if km.keymap_items.keys()[i] == kmi_name:
			if km.keymap_items[i].properties.name == kmi_value:
				return km_item
	return None

def add_hotkey():
	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences
	
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon 
	km = kc.keymaps.new(name="Hide backfacing", space_type='VIEW_3D', region_type='WINDOW')  
	kmi = km.keymap_items.new("object.hide_backfacing",'Q', 'PRESS')     
	#kmi.properties.name = "view3d.hide_backfacing"                           
	kmi.active = True
	addon_keymaps.append((km, kmi))


class BackfaceHidingAddHotkey(bpy.types.Operator):
	''' Add hotkey entry '''
	bl_idname = "backfaceHiding.add_hotkey"
	bl_label = "Addon Preferences Example"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		add_hotkey()

		self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> 3DView -> Mesh")
		return {'FINISHED'}
    
    
def remove_hotkey():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps['3D View Generic']
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_PT_view3d_meshdisplay.append(displayBackfaceHidingPanel)

	# hotkey setup
	add_hotkey()
	

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(displayBackfaceHidingPanel)

	# hotkey cleanup
	remove_hotkey()

	

if __name__ == "__main__":
	register()
