import trimatic
import re
import basic_configuration as bc

stem = trimatic.find_part('Stem Final')
cement = trimatic.find_part('Cement Final')
# head = trimatic.find_part('Head Final')
shaft = trimatic.find_part('Shaft Final')


# def rename_surface(part, name):
#     surfaces = part.get_surfaces()
#     surf_found = False
#     surf_lst = []
#     for surf in surfaces:
#         if re.match('Surface', surf.name) is not None:
#             surf_found = True
#             surf_lst.append(surf)
#     assert surf_found, 'You did not indicate one of the surfaces'
#
#     min_area = 11000
#     for surf in surf_lst:
#         if surf.area<min_area:
#             final_surf = surf
#     final_surf.name = name
#     return None
#
#
# rename_surface(shaft, 'Bottom')
# rename_surface(stem, 'Load')
# rename_surface(head, 'Load')

#Create head load point
# head_d=trimatic.duplicate(head)
# head_surfs = head_d.get_surfaces()
# for surf in head_surfs:
#     if re.match('[Ll]oad',surf.name) is None:
#         trimatic.delete(surf)
# load_pt = trimatic.compute_center_of_gravity(head_d)
# load_pt = trimatic.create_point(load_pt)
# load_pt.name = 'Load Final'
# trimatic.delete(head_d)

#Create volume meshes
trimatic.remesh.create_volume_mesh(part=shaft, maximum_edge_length=bc.mesh_size)
# trimatic.remesh.create_volume_mesh(part=head, maximum_edge_length=bc.mesh_size)
trimatic.remesh.create_volume_mesh(part=stem, maximum_edge_length=bc.interface_mesh_size)
trimatic.remesh.create_volume_mesh(part=cement, maximum_edge_length=bc.interface_mesh_size)

#Analyze mesh quality
# Check quality of the mesh according to quality measures for Abaqus
maximum_face_angle_n = trimatic.analyze_mesh_quality_volume(shaft,
                                        shape_measure= trimatic.ShapeMeasuresAnalyzeMeshQualityVolume.maximum_face_angle_n,
                                        shape_quality_threshold = 170.00)
minimum_face_angle_a = trimatic.analyze_mesh_quality_volume(shaft,
                              shape_measure=trimatic.ShapeMeasuresAnalyzeMeshQualityVolume.minimum_face_angle_a,
                              shape_quality_threshold=5.00)
abaqus_shape_factor_n = trimatic.analyze_mesh_quality_volume(shaft,
                                shape_measure=trimatic.ShapeMeasuresAnalyzeMeshQualityVolume.abaqus_shape_factor_n,
                                shape_quality_threshold=0.0001)
edge_ratio_a = trimatic.analyze_mesh_quality_volume(shaft,
                                shape_measure=trimatic.ShapeMeasuresAnalyzeMeshQualityVolume.edge_ratio_a,
                                shape_quality_threshold=10.00)


if maximum_face_angle_n[1] == 100:
    print("Femur shaft: Maximum face angle (N): all passed")
if minimum_face_angle_a[1] == 0:
    print("Femur shaft: Minimum face angle (A): all passed")
if abaqus_shape_factor_n[1] == 0:
    print("Femur shaft: Abaqus shape factor (N): all passed")
if edge_ratio_a[1] == 100:
    print("Femur shaft: Edge ratio (A): all passed")

