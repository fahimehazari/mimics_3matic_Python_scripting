root_folder_scripts = sys.path[0]
#TODO: should be present automatic (we now install)
sys.path.append(os.path.join(root_folder_scripts,'..','..','..'))

import my_math as mm
import basic_configuration as bc
import trimatic
import math
import json
import glob
import numpy
from stl import mesh

# some shortcuts
class Prop: pass
class Ref: pass

#######################################################################################################
###################### Defining functions #############################################################
#######################################################################################################

def find_part_several_names(list_of_names):
    # Parts are not always consequently named in the available projects: this function finds a part based on a list of
    # several possible names.
    obj_found = False
    for name in list_of_names:
        if trimatic.find_part(name) is not None:
            if obj_found is True:
                assert False, "More than 1 object with given name " + str(list_of_names) + " found"
            name_part = name
            obj_found = True
    if obj_found is True:
        return trimatic.find_part(name_part)
    assert False, "No objects with given names " + str(list_of_names) + " found"

def find_point_several_names(list_of_names):
    # Landmarks are not always consequently named in the available projects: this function finds a point based on a list of
    # several possible names.
    obj_found = False
    for name in list_of_names:
        if trimatic.find_point(name) is not None:
            if obj_found is True:
                assert False, "More than 1 object with given names " + str(list_of_names) + " found"
            name_point = name
            obj_found = True
    if obj_found is True:
        return trimatic.find_point(name_point)
    else:
        assert False, "No objects with given names " + str(list_of_names) + " found"

def addition(u,v):
    return [ u[i]+v[i] for i in range(len(u)) ]

def subtraction(u, v):
    return [ u[i]-v[i] for i in range(len(u)) ]

def multiplication(u, k):
    return [ u[i]*k  for i in range(len(u)) ]

def dotproduct(u, v):
    return sum(u[i]*v[i] for i in range(len(u)))

def crossproduct(a, b):
    assert len(a) == len(b) == 3, 'For 3D vectors only'
    a1, a2, a3 = a
    b1, b2, b3 = b
    return [a2*b3 - a3*b2, a3*b1 - a1*b3, a1*b2 - a2*b1]

def point_to_line_projection(pt, origin, direction):
    ap = subtraction(pt, origin)
    dp = dotproduct(ap, direction) / dotproduct(direction, direction)
    return addition(origin, multiplication(direction, dp))

def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def translate_from_point_to_point(entities,point_from,point_to,number_of_copies = 0):
    trimatic.utils.check_license('translate', '3-matic Base')

    translation_vector = [0,0,0]
    for i in range(3):
        translation_vector[i] = point_to[i] - point_from[i]
    return trimatic.translate(trimatic.single_or_multiple_entities(entities),trimatic.point_argument(translation_vector),number_of_copies)

def line_plane_intersection(p0, p1, p_co, p_no, epsilon=1e-6):
    """
    p0, p1: define the line
    p_co, p_no: define the plane:
        p_co is a point on the plane (plane coordinate).
        p_no is a normal vector defining the plane direction; does not need to be normalized.

    return a Vector or None (when the intersection can't be found).
    """

    u = subtraction(p1, p0)
    dotp = dotproduct(p_no, u)

    if math.fabs(dotp) > epsilon:
        # the factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = subtraction(p0, p_co)
        fac = -dotproduct(p_no, w) / dotp
        u = multiplication(u, fac)
        return addition(p0, u)
    else:
        # The segment is parallel to plane
        return None


#######################################################################################################
###################### Main script ####################################################################
#######################################################################################################
# This script starts from implanted femurs placed in the folder "Datasets\Mimics". For each of the femur-
# implant combinations an osteotomy cut is performed, a NMA is created and the parts are meshed into
# linear tetrahedral volume elements.

# Set path
root_folder = r"C:\Users\jeroen\Documents\Thesis\Patient data\UZBrussel projects\Mesh creation"
source_folder = os.path.join(root_folder, "Datasets\Mimics") #the prepared files were placed in this folder
derived_folder = os.path.join(root_folder, "Meshed femurs") # output projects will be placed in this folder
if not os.path.exists(derived_folder):
        os.mkdir(derived_folder) #if the folder "Femurs with measurements" does not yet exist, the folder is created
mcs_source_file = os.path.join(source_folder, "*.mcs")
print("Start mesh creation")

# Iterate over all the source 3-matic files
mcs_files = sorted(glob.glob(mcs_source_file)) #return a possibly-empty list of path names that match 'mxp_source_file'
for mcs_file_name in mcs_files:
    trimatic.new_project()
    trimatic.import_project(mcs_file_name)
    project_name = os.path.split(mcs_file_name)[1][:-4]
    print(project_name)

# Create subfolder for saving the resulting files
    index_end_bone = project_name.find(" - ")
    index_end_implant= project_name.find((" - "),index_end_bone+3)
    bone_name = project_name[0:index_end_bone]
    implant_name = project_name[index_end_bone+3:index_end_implant]
    bone_derived_folder = os.path.join(derived_folder, bone_name)  # projects will be placed in this folder
    if not os.path.exists(bone_derived_folder):
        os.mkdir(bone_derived_folder)

# Read json file
    source_folder_ref = r"C:\MedData\UZBrussel projects\Femur references"  # JSON files with information of landmarks and anatomical measurements
    reference_file_name = os.path.join(source_folder_ref, bone_name + ".json")
    with open(reference_file_name) as data_file:
        refs = json.load(data_file)
        ref = Ref()
        ref.mid_point_epicon = refs["Mid_point_epicon"]
        ref.intersection_point = refs["Intersection_point"]
        ref.MC = refs["Med_post_con"]
        ref.LC = refs["Lat_post_con"]

# Find the necessary parts and objects
    implant = trimatic.find_part(implant_name[:-17])
    implant.name = "Implant " + implant.name + "_original"
    implant_head_point_large = find_point_several_names([implant_name + " - Head center Large", implant_name + " - Head center Large "])
    collar = trimatic.find_point(implant_name + " - Collar")
    femur = find_part_several_names(['Femur', 'Full femur', 'Full Femur'])
    femur.name = "Femur"
    trabecular = find_part_several_names(["Trabecular", "Trabecular bone"])
    trabecular.name = "Trabecular"
    head = find_point_several_names(["Head", "head", "Head_center", "Head-center", "Head center"])
    ME = trimatic.find_point("Med_epicon")
    LE = trimatic.find_point("Lat_epicon")
    implant_central_axis_line = trimatic.find_line(implant_name + " - Central implant axis")
    implant_central_axis_line.length = implant_central_axis_line.length * 3
    implant_taper_center_line = trimatic.find_line(implant_name + " - Implant taper center line")
    implant_taper_center_line.length = 100
    implant_reference_pl = trimatic.find_plane(implant_name + " - Implant reference plane")
    proximal_femoral_axis = trimatic.find_line("Proximal femoral axis")
    fossa_troch = trimatic.find_point("Fossa_troch")
    mid_point_epicon = trimatic.create_point(ref.mid_point_epicon)
    mid_point_epicon.name = "Mid point epicon"

########################################
##### Merge surfaces implant ###########

# This step is needed because the surface of the original implant has intersection contours that lead to a bad mesh
    surfaces = implant.find_surfaces(".*")
    min_error = 99999
    for surf in surfaces:
        if surf.area == 0:
            trimatic.delete(surf)
        pl = trimatic.create_plane_fit(surf)
        normal = pl.normal
        if mm.dot(normal,implant_taper_center_line.direction) < 0:
            normal = mm.mul(normal,-1)
        error = mm.distance(normal,implant_taper_center_line.direction)
        if error < min_error:
            top_implant = surf
            min_error = error
    top_implant.name = "Top"
    surfaces = implant.find_surfaces("Surface.*")
    shaft_implant = trimatic.data.merge(surfaces)
    shaft_implant.name = "Shaft"

########################################
####### Identify imlant tip ############

    bottom_implant = implant.find_surface("Bottom")
    bottom_implant_plane = trimatic.create_plane_fit(bottom_implant)
    bottom_implant_plane_copy = trimatic.duplicate(bottom_implant_plane)
    bottom_implant_plane_copy.name = ("Implant bottom plane")
    top_point_projection = mm.point_to_plane_projection(implant_head_point_large.coordinates,bottom_implant_plane.origin,bottom_implant_plane.normal)
    implant_length = mm.distance(implant_head_point_large.coordinates,top_point_projection)
    tip_length = (1.5/9.5)*implant_length
    translation_vector = mm.mul(implant_central_axis_line.direction,tip_length)
    translation_vector = mm.mul(translation_vector,-1)
    trimatic.translate(bottom_implant_plane,translation_vector)
    bottom_implant_plane.name = "Implant mid-tip plane"
    trimatic.create_intersection_curve(entity_set1=implant, entity_set2=bottom_implant_plane)
    surfaces = implant.find_surfaces("Shaft.*")
    min_surf_index = 0
    max_surf_index = 0
    for i,surf in enumerate(surfaces):
        if surf.area < surfaces[min_surf_index].area:
            min_surf_index = i
        if surf.area > surfaces[max_surf_index].area:
            max_surf_index = i
    shaft_implant = surfaces[max_surf_index]
    shaft_implant.name = "Shaft"
    tip_implant = surfaces[min_surf_index]
    tip_implant.name = "Tip"
    trimatic.data.merge([implant.find_surface("Tip"),implant.find_surface("Bottom")])

########################################
#### Clean-up unnecessary objects ######

    # Clean-up file
    list_of_objects = [];
    list_of_objects.append(femur)
    list_of_objects.append(trabecular)
    list_of_objects.append(implant)
    list_of_objects.append(collar)
    list_of_objects.append(implant_central_axis_line)
    list_of_objects.append(implant_taper_center_line)
    list_of_objects.append(implant_reference_pl)
    list_of_objects.append(proximal_femoral_axis)
    list_of_objects.append(bottom_implant_plane)
    list_of_objects.append(bottom_implant_plane_copy)
    list_of_objects.append(fossa_troch)
    objects = list(trimatic.objects())
    for o in objects:
        if o in list_of_objects:
            continue
        try:
            trimatic.delete(o)
        except:
            pass

########################################
###### Wrapping and smoothing ##########

    wrapped_femur=trimatic.design.wrap(entities=femur,gap_closing_distance=0.5,smallest_detail=0.5)
    femur.visible = False
    femur.name = "femur_original"
    wrapped_femur.visible=False
    smoothed_femur=trimatic.data.duplicate(entities=wrapped_femur)
    smoothed_femur.name=wrapped_femur.name+"_smoothed"
    trimatic.fix.smooth(entities=smoothed_femur,smooth_factor=0.3)

    trabecular.visible = False
    trabecular.name = "trabecular_original"

########################################
###### Identify femoral condyles #######

    # Identify femoral condyles for boundary conditions in the FEA
    z_axis_femur = trimatic.create_line(ref.mid_point_epicon, ref.intersection_point) #z-axis as described in Bergmann (2001)
    z_axis_femur.name = "z-axis Bergmann"
    condylar_plane = trimatic.create_plane_normal_origin(z_axis_femur.direction, ref.mid_point_epicon)
    move_up_distance = 30;
    translation_vector = mm.mul(z_axis_femur.direction, move_up_distance)
    trimatic.translate(condylar_plane, translation_vector)
    trimatic.create_intersection_curve(entity_set1=smoothed_femur, entity_set2=condylar_plane)
    surfaces = smoothed_femur.find_surfaces("Surface.*")
    min_surf_index = 0
    max_surf_index = 0
    for i, surf in enumerate(surfaces):
        if surf.area < surfaces[min_surf_index].area:
            min_surf_index = i
        if surf.area > surfaces[max_surf_index].area:
            max_surf_index = i
    shaft_femur = surfaces[max_surf_index]
    shaft_femur.name = "Femur shaft"
    condyles_femur = surfaces[min_surf_index]
    condyles_femur.name = "Femur condyles"

########################################
##### Identify hip contact surface #####

    # Identify surface on the femoral head for applying the hip contact force in the FEA
    top_implant = implant.find_surface("Top")
    top_implant_plane = trimatic.create_plane_fit(top_implant)
    trimatic.create_intersection_curve(entity_set1=smoothed_femur, entity_set2=top_implant_plane)
    surfaces = smoothed_femur.find_surfaces("Femur shaft.*")
    min_surf_index = 0
    max_surf_index = 0
    for i, surf in enumerate(surfaces):
        if surf.area < surfaces[min_surf_index].area:
            min_surf_index = i
        if surf.area > surfaces[max_surf_index].area:
            max_surf_index = i
    shaft_femur = surfaces[max_surf_index]
    shaft_femur.name = "Femur shaft"
    hip_contact_surface = surfaces[min_surf_index]
    hip_contact_surface.name = "Hip contact"

########################################
######### Surface remesh ###############

# This is done before making the osteotomy cut to have a more optimal mesh
    implant.visible = False
    smoothed_femur.visible = False
    remeshed_femur = trimatic.data.duplicate(smoothed_femur)
    remeshed_implant = trimatic.data.duplicate(implant)
    remeshed_femur.name = smoothed_femur.name + "_remeshed"
    remeshed_implant.name = "Implant " + implant_name[:-17] + "_remeshed"

    k = bc.meshsize
    if k <= 2:
        corr1 = (-k + 3)
        corr2 = (-k + 2)
    else:
        corr1 = 0
        corr2 = 0

    # femur
    trimatic.adaptive_remesh(entities=remeshed_femur, target_triangle_edge_length=k - 2 + corr1,
                             preserve_surface_contours=False)
    remeshed_femur = trimatic.uniform_remesh(entities=remeshed_femur, target_triangle_edge_length=k - 1 + corr2)

    # implant
    trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=k - 2 + corr1,
                             preserve_surface_contours=True)
    trimatic.adaptive_remesh(entities=[remeshed_implant.find_surface("Top"), remeshed_implant.find_surface("Taper"),
                                       remeshed_implant.find_surface("Shaft")],
                             target_triangle_edge_length=k - 2 + corr1, preserve_surface_contours=False)
    trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=k - 1 + corr2,
                             preserve_surface_contours=True)
    trimatic.adaptive_remesh(entities=[remeshed_implant.find_surface("Top"), remeshed_implant.find_surface("Taper"),
                                       remeshed_implant.find_surface("Shaft")],
                             target_triangle_edge_length=k - 1 + corr2, preserve_surface_contours=False)
    trimatic.fix.smooth(remeshed_implant, 0.3)
    trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=k - 1 + corr2,
                             preserve_surface_contours=True)

    if remeshed_femur:
       remeshed_femur=trimatic.data.find_object(smoothed_femur.name+"_remeshed")
       #fix the mesh
       remeshed_femur.visible=False
       fixed_femur=trimatic.data.duplicate(remeshed_femur)
       fixed_femur.name=remeshed_femur.name+"_fixed"
       trimatic.fix.auto_fix(entities=fixed_femur)

    if remeshed_implant:
       remeshed_implant=trimatic.data.find_object("Implant " + implant_name[:-17] + "_remeshed")
       #fix the mesh
       remeshed_implant.visible=False
       fixed_implant=trimatic.data.duplicate(remeshed_implant)
       fixed_implant.name=remeshed_implant.name+"_fixed"
       trimatic.fix.auto_fix(entities=fixed_implant)


########################################
###### Osteotomy cut ##################

    if bc.position_variation_mode == False:
        # Find origin of implant coordinate system
        implant_coord_system = implant.object_coordinate_system
        origin = implant_coord_system.origin
        origin_point = trimatic.create_point(origin)
        origin_point.name = "Origin coord system"

        origin_point.visible = False
        implant_reference_pl.visible = False

        # Define osteotomy plane
        #osteotomy_plane = trimatic.create_plane_normal_origin(implant_taper_center_line.direction, collar)
        osteotomy_plane = trimatic.create_plane_normal_origin(implant_taper_center_line.direction, origin)
        osteotomy_plane.name = "Osteotomy plane"
        osteotomy_plane.delta_x = 100
        osteotomy_plane.delta_y = 100

        # Find intersection point of osteotomy plane and taper center line of implant
        osteotomy_point_coord = line_plane_intersection(implant_taper_center_line.get_point(0),implant_taper_center_line.get_point(1),
                                                  osteotomy_plane.origin, osteotomy_plane.normal)
        osteotomy_point = trimatic.create_point(osteotomy_point_coord)
        osteotomy_point.name = "Osteotomy point"

        # Define trochanter plane (an extra cut is made to keep the trochanter intact)
        if mm.dot(proximal_femoral_axis.direction,z_axis_femur.direction) < 0:
            print("Femoral axis direction switched")
            point1 = proximal_femoral_axis.get_point(0)
            point2 = proximal_femoral_axis.get_point(1)
            trimatic.delete(proximal_femoral_axis)
            proximal_femoral_axis = trimatic.create_line(point2,point1)
            proximal_femoral_axis.name = "Proximal femoral axis"
        fossa_troch_3cm = trimatic.duplicate(fossa_troch)
        trimatic.translate(fossa_troch_3cm, multiplication(proximal_femoral_axis.direction,30), number_of_copies=0)
        fossa_troch_3cm.name = "Fossa troch 3cm translation"
        trochanter_plane = trimatic.create_plane_2_points_perpendicular_1_plane(fossa_troch,fossa_troch_3cm,implant_reference_pl)
        trochanter_plane.name = "Trochanter plane"
        trochanter_plane.delta_x = 100
        trochanter_plane.delta_y = 100

        # Find the intersection of the osteotomy plane and the trochanter plane
        intersection_line = trimatic.create_line_plane_intersection(osteotomy_plane,trochanter_plane)
        intersection_line.name = "Osteotomy intersection line"

        # Find points needed to create the stl
        parallel_intersection_line_ost_pl = trimatic.create_line_direction_and_length(collar,intersection_line.direction,50)
        point1 = intersection_line.get_point(0)
        point2 = intersection_line.get_point(1)
        point1_projection_ost_pl = point_to_line_projection(point1,parallel_intersection_line_ost_pl.get_point(0),parallel_intersection_line_ost_pl.direction)
        direction_ost_pl = subtraction(point1_projection_ost_pl,point1)
        trimatic.translate(parallel_intersection_line_ost_pl,multiplication(direction_ost_pl,5))
        point3 = point_to_line_projection(point1,parallel_intersection_line_ost_pl.get_point(0),parallel_intersection_line_ost_pl.direction)
        point4 = point_to_line_projection(point2,parallel_intersection_line_ost_pl.get_point(0),parallel_intersection_line_ost_pl.direction)

        parallel_intersection_line_troch_pl = trimatic.create_line_direction_and_length(fossa_troch,intersection_line.direction,50)
        #parallel_intersection_line_troch_pl = trimatic.create_line_direction_and_length(fossa_troch_3cm,intersection_line.direction, 50)
        point1_projection_troch_pl = point_to_line_projection(point1,parallel_intersection_line_troch_pl.get_point(0),parallel_intersection_line_troch_pl.direction)
        direction_troch_pl = subtraction(point1_projection_troch_pl,point1)
        if mm.dot(direction_troch_pl,proximal_femoral_axis.direction) < 0:
            direction_troch_pl = mm.mul(direction_troch_pl,-300)
        trimatic.translate(parallel_intersection_line_troch_pl,mm.mul(direction_troch_pl,0.2))
        #trimatic.translate(parallel_intersection_line_troch_pl, mm.mul(direction_troch_pl, 1.5))
        point5 = point_to_line_projection(point1,parallel_intersection_line_troch_pl.get_point(0),parallel_intersection_line_troch_pl.direction)
        point6 = point_to_line_projection(point2,parallel_intersection_line_troch_pl.get_point(0),parallel_intersection_line_troch_pl.direction)
        
        # Create an stl for the osteotomy cut
        data = numpy.zeros(4, dtype=mesh.Mesh.dtype)

        #osteotomy plane
        data['vectors'][0] = numpy.array([[point1[0],point1[1], point1[2]],
                                          [point2[0], point2[1], point2[2]],
                                          [point3[0], point3[1], point3[2]]])
        data['vectors'][1] = numpy.array([[point2[0], point2[1], point2[2]],
                                          [point3[0], point3[1], point3[2]],
                                          [point4[0], point4[1], point4[2]]])
        #trochanter plane
        data['vectors'][2] = numpy.array([[point1[0],point1[1], point1[2]],
                                          [point2[0], point2[1], point2[2]],
                                          [point5[0], point5[1], point5[2]]])
        data['vectors'][3] = numpy.array([[point2[0], point2[1], point2[2]],
                                          [point5[0], point5[1], point5[2]],
                                          [point6[0], point6[1], point6[2]]])

        your_mesh = mesh.Mesh(data, remove_empty_areas=False)
        stl_filename = os.path.join(bone_derived_folder, "Osteotomy " +  project_name[:index_end_implant]  + ".stl")
        your_mesh.save(stl_filename)

    else:
        stl_filename = os.path.join(source_folder, "Osteotomy " +  project_name[:index_end_implant]  + ".stl")

    trimatic.import_part_stl(stl_filename,fix_normals=True)
    osteotomy = trimatic.find_part(os.path.split(stl_filename)[1][:-4])

    # Make the cut
    cut_parts = trimatic.cut(fixed_femur,osteotomy)
    if cut_parts[0].volume > cut_parts[1].volume:
        femur_head = cut_parts[1]
        femur_shaft = cut_parts[0]
    else:
        femur_head = cut_parts[0]
        femur_shaft = cut_parts[1]

    # Rename surfaces of the femoral components
    femur_hip_contact_surface = femur_head.find_surface("Hip contact")
    femur_head_outer_surface = femur_head.find_surface("Femur shaft")
    femur_head_outer_surface.name = "Femur head"
    femur_head_osteotomy_surface = femur_head.find_surface("Surface")
    femur_head_osteotomy_surface.name = "Osteotomy"

    femur_shaft_osteotomy_surface = femur_shaft.find_surface("Surface")
    femur_shaft_osteotomy_surface.name = "Osteotomy"

    # Set visibility of several parts off
    fixed_femur.visible = False
    fixed_implant.visible = False
    osteotomy.visible = False
    femur_head.name = "Femur head"
    femur_shaft.name = "Femur shaft"
    implant = trimatic.duplicate(fixed_implant)
    implant.name = "Implant"
    femur_head.visible = False
    femur_shaft.visible = False

    # Clean up file
    if bc.position_variation_mode == False:
        trimatic.delete(trochanter_plane)
        trimatic.delete(parallel_intersection_line_ost_pl)
        trimatic.delete(parallel_intersection_line_troch_pl)
        trimatic.delete(fossa_troch_3cm)
    trimatic.delete(fossa_troch)
    trimatic.delete(proximal_femoral_axis)
    trimatic.delete(implant_reference_pl)
    trimatic.delete(z_axis_femur)

#################################
########### NMA #################

    #implant_copy = trimatic.data.duplicate(implant)
    #femur_shaft_copy = trimatic.data.duplicate(femur_shaft)
    #femur_head_copy = trimatic.data.duplicate(femur_head)

    nma = trimatic.create_non_manifold_assembly(femur_shaft, [femur_head, implant])
    assert nma is not None, "the NMA failed"
    nma.name = 'Non-manifold assembly'

    # Rename surfaces of the NMA
    surfaces = nma.find_surfaces(".*")
    for surf in surfaces:
        if surf.area == 0:
            trimatic.delete(surf)
    femur_head_surf = nma.find_surfaces("Femur head.*") # sometimes the name deviates and has a number attached "Femur head - 0"
    # (this is due to emptie surfaces that were created with the osteotomy cut)
    assert len(femur_head_surf) == 1, "More femur head surfaces have been found in the assembly"
    femur_head_surf = femur_head_surf[0]
    femur_head_surf.name = "Femur head"
    femur_shaft_surf = nma.find_surfaces("Femur shaft.*")
    assert len(femur_shaft_surf) == 1, "More femur shaft surfaces have been found in the assembly"
    femur_shaft_surf = femur_shaft_surf[0]
    femur_shaft_surf.name = "Femur shaft"
    osteotomy_surf = nma.find_surfaces("Osteotomy.*")
    assert len(osteotomy_surf) == 1, "More osteotomy surfaces have been found in the assembly"
    osteotomy_surf = osteotomy_surf[0]
    osteotomy_surf.name = "Osteotomy"
    femur_con_surf = nma.find_surface("Femur condyles")
    hip_contact_surf = nma.find_surface("Hip contact")
    taper_surf = nma.find_surface("Taper")
    tip_surf = nma.find_surface("Tip")
    top_surf = nma.find_surface("Top")

    # The shaft of the implant has several surfaces: interface with femur_shaft and femur_head, and
    # sometimes also a piece that sticks outside the bone. Each surface is identified in a robust way.
    implant_shaft_surfaces = nma.find_surfaces("Shaft.*")
    min_error_neck = 999999
    min_error_shaft = 99999
    for i,surf in enumerate(implant_shaft_surfaces):
        line = trimatic.create_line_fit_ruled_surface(surf)
        line_dir = line.direction
        if mm.dot(line_dir,implant_taper_center_line.direction) < 0:
            line_dir = mm.mul(line_dir,-1)
        error_neck = mm.distance(line_dir,implant_taper_center_line.direction)
        if error_neck < min_error_neck:
            implant_neck_index = i
            min_error_neck = error_neck
        if mm.dot(line_dir, implant_central_axis_line.direction) < 0:
            line_dir = mm.mul(line_dir, -1)
        error_shaft = mm.distance(line_dir, implant_central_axis_line.direction)
        if error_shaft < min_error_shaft:
            implant_shaft_index = i
            min_error_shaft = error_shaft
    implant_neck_surf = implant_shaft_surfaces[implant_neck_index]
    implant_shaft_surf = implant_shaft_surfaces[implant_shaft_index]
    assert len(implant_shaft_surfaces) < 4, "The implant has more parts that stick out of the bone"
    if len(implant_shaft_surfaces) == 3:
        for i in range(0,3):
            if i not in [implant_neck_index,implant_shaft_index]:
                implant_out_index = i
        implant_out_surf = implant_shaft_surfaces[implant_out_index]
        implant_out_surf.name = "Implant outside"
    implant_neck_surf.name = "Implant neck"
    implant_shaft_surf.name = "Implant shaft"

    # Clean up
    parts = trimatic.parts()
    objects = list(trimatic.objects())
    for o in objects:
        if o in parts or o in [bottom_implant_plane, bottom_implant_plane_copy, osteotomy_point, osteotomy_plane]:
            continue
        try:
            trimatic.delete(o)
        except:
            pass

    # Define the local parameters for the adaptive remesh
    local_parameters_list = []
    for i in range(0, len(implant_shaft_surfaces)):
        local_parameters_list.append((implant_shaft_surfaces[i], k - 1 + corr2, 0.0))
    local_parameters_list.append((osteotomy_surf, k - 1 + corr2, 0.0))
    local_parameters_list.append((top_surf, k - 1 + corr2, 0.0))
    local_parameters_list.append((taper_surf, k - 1 + corr2, 0.0))
    local_parameters_list.append((tip_surf, k - 1 + corr2, 0.0))

    # Remesh NMA
    remeshed_nma = trimatic.adaptive_remesh(entities=nma, target_triangle_edge_length=k-1+corr2,
                                            preserve_surface_contours=False)
    assert remeshed_nma == True, "Adaptive remesh of NMA failed"
    remeshed_nma = trimatic.adaptive_remesh(entities=nma, target_triangle_edge_length=k,
                                            preserve_surface_contours=True,
                                            local_remesh_parameters=tuple(local_parameters_list), local_growth_rate=30)
    assert remeshed_nma == True, "Adaptive remesh of NMA failed"
    remeshed_nma = trimatic.adaptive_remesh(entities=nma, target_triangle_edge_length=k,
                                            preserve_surface_contours=False,
                                            local_remesh_parameters=tuple(local_parameters_list), local_growth_rate=30)
    assert remeshed_nma == True, "Adaptive remesh of NMA failed"


    # Split NMA
    femur_part = trimatic.duplicate(nma)
    femur_part.name = "Femur_shaft"
    trimatic.delete(femur_part.find_surface("Top"))
    trimatic.delete(femur_part.find_surface("Taper"))
    trimatic.delete(femur_part.find_surface("Implant neck"))
    if len(implant_shaft_surfaces) == 3:
        trimatic.delete(femur_part.find_surface("Implant outside"))
    trimatic.delete(femur_part.find_surface("Femur head"))
    trimatic.delete(femur_part.find_surface("Hip contact"))
    trimatic.auto_fix(femur_part)

    head_part = trimatic.duplicate(nma)
    head_part.name = "Femur_head"
    trimatic.delete(head_part.find_surface("Implant shaft"))
    trimatic.delete(head_part.find_surface("Tip"))
    if len(implant_shaft_surfaces) == 3:
        trimatic.delete(head_part.find_surface("Implant outside"))
    trimatic.delete(head_part.find_surface("Femur shaft"))
    trimatic.delete(head_part.find_surface("Femur condyles"))
    trimatic.auto_fix(head_part)

    implant_part = trimatic.duplicate(nma)
    implant_part.name = "Implant"
    trimatic.delete(implant_part.find_surface("Femur head"))
    trimatic.delete(implant_part.find_surface("Hip contact"))
    trimatic.delete(implant_part.find_surface("Femur shaft"))
    trimatic.delete(implant_part.find_surface("Femur condyles"))
    trimatic.delete(implant_part.find_surface("Osteotomy"))
    trimatic.auto_fix(implant_part)

    nma.visible = False

#################################
######### Volume mesh ###########

    final_shaft = trimatic.find_part("Femur_shaft")
    final_implant = trimatic.find_part("Implant")
    final_head = trimatic.find_part("Femur_head")
    trimatic.remesh.create_volume_mesh(part=final_shaft, maximum_edge_length=k)
    trimatic.remesh.create_volume_mesh(part=final_head, maximum_edge_length=k)
    trimatic.remesh.create_volume_mesh(part=final_implant, maximum_edge_length=k)

    # Check quality of the mesh according to quality measures for Abaqus
    maximum_face_angle_n = trimatic.analyse_mesh_quality(trimatic.find_part("Femur_shaft"),
                                            shape_measure= trimatic.ShapeMeasuresAm.maximum_face_angle_n,
                                            shape_quality_threshold = 170.00, analyse_volume_when_available = True)
    minimum_face_angle_a = trimatic.analyse_mesh_quality(trimatic.find_part("Femur_shaft"),
                                  shape_measure=trimatic.ShapeMeasuresAm.minimum_face_angle_a,
                                  shape_quality_threshold=5.00, analyse_volume_when_available=True)
    abaqus_shape_factor_n = trimatic.analyse_mesh_quality(trimatic.find_part("Femur_shaft"),
                                    shape_measure=trimatic.ShapeMeasuresAm.abaqus_shape_factor_n,
                                    shape_quality_threshold=0.0001, analyse_volume_when_available=True)
    edge_ratio_a = trimatic.analyse_mesh_quality(trimatic.find_part("Femur_shaft"),
                                    shape_measure=trimatic.ShapeMeasuresAm.edge_ratio_a,
                                    shape_quality_threshold=10.00, analyse_volume_when_available=True)


    if maximum_face_angle_n[1] == 100:
        print("Femur shaft: Maximum face angle (N): all passed")
    if minimum_face_angle_a[1] == 0:
        print("Femur shaft: Minimum face angle (A): all passed")
    if abaqus_shape_factor_n[1] == 0:
        print("Femur shaft: Abaqus shape factor (N): all passed")
    if edge_ratio_a[1] == 100:
        print("Femur shaft: Edge ratio (A): all passed")

#################################
######## Save file ##############

    mxp_output_file = os.path.join(bone_derived_folder, project_name[:-25] + ".mxp")
    if os.path.exists(mxp_output_file):
        os.remove(mxp_output_file) #delete file if it already exists
    trimatic.save_project_as(mxp_output_file)

    #retain only the volume meshes for import into mimics
    objects = list(trimatic.objects())
    for o in objects:
        if o not in [final_shaft,final_head,final_implant, bottom_implant_plane, bottom_implant_plane_copy, osteotomy_point, osteotomy_plane]:
            trimatic.delete(o)
    mxp_output_file_for_mimics = os.path.join(bone_derived_folder, project_name + ".mxp")
    if os.path.exists(mxp_output_file_for_mimics):
        os.remove(mxp_output_file_for_mimics) #delete file if it already exists
    trimatic.save_project_as(mxp_output_file_for_mimics)


print("Done")
