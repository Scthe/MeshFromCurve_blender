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
    "author": "Marcin Matusczyk (Scthe)",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Mesh From Curve",
    "description": "Create Mesh based on curve",
    "warning": "",
    "wiki_url": "",
    "category": "Tools"}

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty
import cmath
import logging

log = logging.getLogger(__name__)



#####################
### Create final object

def set_object_center(obj, vertices, center):
    obj.location = center
    # translation from global to local system
    for vID in range(len(vertices)):
        for i in range(3):
            vertices[vID][i] -= center[i]

def create_mesh_edges_only(mesh, vertices, segment_count):
    edges = []
    for vID in range(1, len(vertices)):
        if vID % segment_count == 0:
            continue
        edges.append([vID - 1, vID])
    return edges

def create_mesh_with_faces(vertices, curves_count, segment_count):
    def create_face_indices(baseIdx):
        return (baseIdx,
                baseIdx + 1,
                baseIdx + segment_count + 1,
                baseIdx + segment_count)

    faces = []
    for i in range(segment_count - 1): # go all the way around
        for j in range(curves_count - 1):
            base = j * segment_count + i
            if (base + 1) % segment_count == 0: # do not connect first and last
                continue
            face = create_face_indices(base)
            faces.append(face)
    return faces

def create_object(context, center, vertices, curves_count, segment_count):
    context = context or bpy.context
    scene = context.scene
    layer = context.view_layer
    layer_collection = context.layer_collection or layer.active_layer_collection
    scene_collection = layer_collection.collection

    mesh = bpy.data.meshes.new("mesh_from_curve_mesh")
    obj = bpy.data.objects.new('mesh_from_curve_object', mesh)
    scene.collection.objects.link(obj)   # add the data to the scene as an object
    obj.show_wire = True
    set_object_center(obj, vertices, center)

    if curves_count == 1:
        edges = create_mesh_edges_only(mesh, vertices, segment_count)
        faces = []
    else:
        edges = []
        faces = create_mesh_with_faces(vertices, curves_count, segment_count)

    mesh.from_pydata(vertices, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)

    obj.select_set(True)
    layer.update() # apply location
    layer.objects.active = obj


#####################
### Utils

def distance(p1, p2):
    ''' :p1, :p2 <- arrays of 3 values [x, y, z] '''
    #return cmath.sqrt(sum( [ (a-b)**2 for a,b in zip(p1, p2) ] ))
    L = [ p1[0] - p2[0] , p1[1] - p2[1] , p1[2] - p2[2] ]
    return abs( cmath.sqrt( L[0]*L[0] + L[1]*L[1] + L[2]*L[2]) )

def deselect_all():
    ''' deselect all objects '''
    bpy.ops.object.select_all(action='DESELECT')

def select_only(obj):
    ''' select one object '''
    deselect_all()
    obj.select_set(True)

def report_error(operator, msg):
    if operator is not None:
        operator.report({'ERROR_INVALID_CONTEXT'}, msg)
    log.error('[ERROR] ' + msg)

def get_world_position(obj, vert_idx):
    wmtx = obj.matrix_world
    co = obj.data.vertices[vert_idx].co
    return [e.real for e in (wmtx @ co)]


#####################
### Calculate positions of vertices - main part of this script

def get_curve_vertices(obj):
    ''' returns :obj's vertices in expected order and in global coordinates system '''
    vert_cnt = len(obj.data.vertices)
    return [get_world_position(obj, vert_id) for vert_id in range(vert_cnt)]

def get_point_between(start, end, dist):
    ''' point between :start and :end in range of :dist from start '''
    l = [0, 0, 0]
    percent = dist / distance(start, end)

    for i in range (3):
        delta = end[i] - start[i]
        l[i] = start[i] + (percent * delta)
    return l

def calculate_vertices_positions_on_curve(curve_points, segment_length, segment_count):
    result = [curve_points[0]] # add start
    last_original_vertex = 0 # id of last used point from original curve_points collection
    measure_start_point = curve_points[0] # coordinates from which we start measurement

    for i in range(segment_count - 2):
        next_point_in = segment_length  # distance to next point
        to_next_orginal_vertex  = distance(
            measure_start_point,
            curve_points[last_original_vertex + 1]
        )

        # move along the curve till we find segment into which we will add vertex
        while next_point_in > to_next_orginal_vertex:
            last_original_vertex += 1
            measure_start_point = curve_points[last_original_vertex]
            next_point_in -= to_next_orginal_vertex
            to_next_orginal_vertex  = distance(
                measure_start_point,
                curve_points[last_original_vertex + 1]
            )

        # get vertex position
        p = get_point_between(
            measure_start_point, curve_points[last_original_vertex + 1],
            next_point_in
        )
        measure_start_point = p
        result.append(p)

    result.append(curve_points[-1]) # add end
    return result

def get_curve_length(curve_mesh, cyclic):
    verts = curve_mesh.data.vertices
    total_length = 0

    for vID in range(len(verts) - 1):
        total_length += distance(verts[vID].co, verts[vID + 1].co)

    if cyclic:
        total_length += distance(verts[0].co, verts[-1].co)
    return total_length

def all_selected_are_curves():
    selection = bpy.context.selected_objects
    all_curves = all(o.type == "CURVE" for o in selection)
    return len(selection) > 0 and all_curves

def create_object_from_curves(context, operator, segment_count, cyclic):
    ''' main algorithm '''
    if not all_selected_are_curves():
        report_error(operator, 'Only curves can be selected')
        return False

    # curves can be interpolated. I do not want to write/search for interpolation
    # methods. Convert curves to smooth meshes and use meshes as basis instead
    bpy.ops.object.convert(target = 'MESH', keep_original = True)
    selected_curves = bpy.context.selected_objects

    result_vertices = []
    center = [0, 0, 0]

    for curve in selected_curves:
        select_only(curve)
        bpy.ops.object.transform_apply(location = False, rotation = False, scale = True)

        # get curve props
        total_length = get_curve_length(curve, cyclic)
        segment_length = total_length / (segment_count - 1)
        spline_vertices = get_curve_vertices(curve) # in world coordinates system
        if cyclic:
            starting_vert = get_world_position(curve, 0)
            spline_vertices.append(starting_vert)

        # algorithm
        verts = calculate_vertices_positions_on_curve(spline_vertices, segment_length, segment_count)
        result_vertices.extend(verts)

        for i in range(3):
            center[i] += curve.location[i]

        # cleaning
        bpy.ops.object.delete()

    # end
    center = [c / len(selected_curves) for c in center]
    create_object(
        context,
        center,
        result_vertices,
        len(selected_curves), segment_count
    )
    return True



#####################
### Blender addon

class OBJECT_OT_mesh_from_curve(Operator):
    ''' Create Mesh based on curve '''
    bl_idname = "mesh.mesh_from_curve"
    bl_label = "Mesh From Curve"
    bl_description = "Create Mesh based on curve"
    bl_options = {"REGISTER", "UNDO"}

    segments: IntProperty(
        name="Segments",
        description="Segment count",
        default = 50,
        min = 2,
        max = 1000
    )
    cyclic: BoolProperty(
        name="Cyclic",
        description="Close the shape",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        ok = create_object_from_curves(
            context, self,
            self.segments + 1, self.cyclic
        )
        if not ok:
            return {"CANCELLED"}
        return {"FINISHED"}

def menu_draw (self, context):
    self.layout.operator_context = "INVOKE_REGION_WIN"
    self.layout.operator(
        OBJECT_OT_mesh_from_curve.bl_idname,
        text="Mesh From Curve",
        icon='CURVE_DATA')

def register():
    bpy.utils.register_class(OBJECT_OT_mesh_from_curve)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mesh_from_curve)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_draw)

if __name__ == "__main__":
    # unregister()
    register()
    # create_object_from_curves(None, None, 95, True)
