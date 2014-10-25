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
    "name": "Mesh From Curve",
    "author": "Scthe",
    "version": (0, 1),
    "blender": (2, 72, 0),
    "location": "View3D > Tools -> Create",
    "description": "Create Mesh based on curve",
    "warning": "",
    "wiki_url": "",
    "category": "Tools"}
    
import bpy
from bpy.utils import register_module, unregister_module
from bpy.props import IntProperty
from bpy.props import BoolProperty
import cmath


''' add edge to the mesh '''
def add_edge( mesh, idA, idB):
	mesh.edges.add(1)
	mesh.edges[-1].vertices[0] = idA
	mesh.edges[-1].vertices[1] = idB

def create_mesh( center, vertices, nSegments, add_faces, cyclic, nCurves):
	# base object creation
	mesh = bpy.data.meshes.new("my_mesh")
	obj = bpy.data.objects.new('mfc', mesh)
	bpy.context.scene.objects.link(obj)
	obj.show_wire = True

	obj.location = center			   # location
	for vID in range( len(vertices) ):
		#print ( "v: "+str(vertices[vID]))
		for i in range(3):			  # translation from global to local system
			vertices[vID][i] -= center[i]
			
	#print( "creating mesh: add faces-"+str(add_faces))
	faces = []
	if not add_faces:   # create edges
		for vID in range(1, len(vertices)):
			if vID % nSegments == 0:
				continue
			add_edge( mesh, vID - 1, vID)
	else:			  # add faces	
		for i in range(nSegments -1): # go all the way around
			for j in range(nCurves - 1):
				base = j * nSegments + i
				if (base + 1) % nSegments == 0: # do not connect first and last
					continue
				f =  ( base,\
					base + 1,\
					base + nSegments + 1,\
					base + nSegments )
				faces.append(f)
		if cyclic:
			pass

	mesh.from_pydata( vertices, [], faces)

''' p1, p2 <- arrays of 3 values [x, y, z] '''
def distance( p1, p2):
	#return cmath.sqrt(sum( [ (a-b)**2 for a,b in zip(p1, p2) ] ))
	L = [ p1[0] - p2[0] , p1[1] - p2[1] , p1[2] - p2[2] ]
	return abs( cmath.sqrt( L[0]*L[0] + L[1]*L[1] + L[2]*L[2]) )

''' point between start and end in range of 'dist' from start '''
def getPoint ( start, end, dist ):
	delta = [0, 0, 0]
	l = [0, 0, 0]
	percent = dist / distance(start, end)

	for i in range (3):
		delta[i] = end[i] - start[i]
		l[i] = start[i] + (percent *delta[i])
	return l

''' returns obj's vertices in expected order and in global coordinates system '''
def getSplineVertices( obj):
	wmtx = obj.matrix_world 
	result = []
	for v in obj.data.vertices:
		act = [ e.real for e in (wmtx * v.co)]
		result.append(act)
	return result

''' create mesh'ed version of curve ( assuming that curve is already selected)'''
def create_dummy_object():
	bpy.ops.object.convert( target = 'MESH', keep_original = True )
	obj = bpy.context.object
	
	bpy.ops.object.transform_apply( location = False, rotation = False, scale = True)
	# print("created : " + obj.name)
	return obj

''' deselect all objects TODO: merge with select_only '''
def deselect_all():
	for o in  bpy.data.objects:
		o.select = False

''' select one object '''
def select_only( obj):
	bpy.context.scene.objects.active = obj
	obj.select = False
	obj.select = True

''' create points -> calculate theirs locations '''
def fill_between( org_points, segment_length, nSegments):
	list = []
	segmentID = 0				  # id of last used point from org_points collection
	active_point = org_points[0]	# last added point
	active_segment_len = 0.0001		# overhead from last loop iteration

	for i in range( nSegments - 2):
		next_point_in = segment_length  # distance to next point
		active_segment_len = distance(active_point, org_points[ segmentID + 1])
		while next_point_in > active_segment_len: #and segmentID + 2 < len(SPLINE_VERTICES):
			segmentID += 1 # move to the next segment
			active_point = org_points[segmentID]
			next_point_in -= active_segment_len
			active_segment_len = distance(active_point, org_points[ segmentID + 1])
		p = getPoint(active_point, org_points[segmentID + 1], next_point_in)
		active_point = p
		list.append( p )
	return list

''' main algorithm '''
def curveMesh( nSEGMENTS, cyclic = False):

	#print("\n--------------\n")
	New_Vertices_List = []
	Object_Center = [ 0, 0, 0] # list, so we can add this objects
	
	selected_Curves = [ o for o in bpy.data.objects if o.select and o.type == "CURVE"]
	deselect_all()
	
	for curve in selected_Curves:
		#print('CURVE:' + curve.name)
		
		for i in range(3):
			Object_Center[i] += curve.location[i]
		select_only( curve)
	   
		# create mesh from this curve to iterate easier between points object
		dummy = create_dummy_object()
		curve.select = False
		select_only(dummy)
	
		# Get total length
		total_length = 0
		for vID in range( len (dummy.data.vertices) -1 ): # TODO optimize !
			total_length += distance( dummy.data.vertices[vID].co,\
									  dummy.data.vertices[vID + 1].co )
		if cyclic: total_length += distance( dummy.data.vertices[ 0].co,\
									  dummy.data.vertices[-1].co )
		segment_length = total_length /( nSEGMENTS -1)

		spline_vertices = getSplineVertices( dummy)
		if cyclic:
			wmtx = dummy.matrix_world 
			act = [ e.real for e in (wmtx * dummy.data.vertices[0].co)]
			spline_vertices.append(act)

		# after this, spline_vertices is already in global coordinates system

		# algorithm
		New_Vertices_List.append(spline_vertices[0])
		middle_vertices = fill_between( spline_vertices, segment_length, nSEGMENTS)
		New_Vertices_List.extend(middle_vertices)
		New_Vertices_List.append(spline_vertices[-1]) # !!!
		
		# cleaning
		bpy.ops.object.delete()
		#print()
	
	# end
	Object_Center = [ c / len(selected_Curves) for c in Object_Center] 
	create_mesh( center = Object_Center, vertices = New_Vertices_List, nSegments = nSEGMENTS,\
		add_faces = len(selected_Curves) > 1, cyclic = cyclic, nCurves = len(selected_Curves))

	

class MeshFromCurve(bpy.types.Operator):
	bl_idname = "mesh.meshfromcurve"
	bl_label = "Mesh From Curve"
	bl_description = "Create Mesh based on curve"
	bl_options = {"REGISTER", "UNDO"}

	segments = IntProperty(name="Segments", description="Segment count", default = 50, min = 2, max = 1000)
	#invert = BoolProperty(name="Invert order", description="Try only when everything has failed", default=False) # TODO invert order
	cyclic = BoolProperty(name="Cyclic", description="Is the shape closed ?", default=False)

	@classmethod
	def poll(cls,context):
		return(context.mode == "OBJECT")

	def invoke(self,context, event):
		return self.execute(context)

	def execute(self,context):
		curveMesh(self.segments + 1, self.cyclic)
		return {"FINISHED"}

def menu_draw (self,context):
	self.layout.operator_context = "INVOKE_REGION_WIN"
	self.layout.operator(MeshFromCurve.bl_idname,
        text="Mesh From Curve",
        icon='CURVE_DATA')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_draw)
    bpy.types.VIEW3D_PT_tools_add_object.append(menu_draw)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_draw)
    bpy.types.VIEW3D_PT_tools_add_object.remove(menu_draw)
    

if __name__ == "__main__":
	register()
	#curveMesh( 95,True)
	#print('fin')
	