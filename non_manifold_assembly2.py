import trimatic
import re
import basic_configuration as bc

def create_part_with_surf_name(NMA,name):
    NMA_d = trimatic.duplicate(NMA)
    surface_sets = NMA_d.get_surface_sets()
    for surf in surface_sets:
        if re.match('.*'+name[1:]+'.*',surf.name) is None:
            trimatic.delete(surf)
    NMA_d.name = name+' Final'
    trimatic.auto_fix(NMA_d) #For inverted normals
    return merge_surface_sets(NMA_d)

def merge_surface_sets(part):
    surf_sets=part.get_surface_sets()
    for surf_set in surf_sets:
        surfaces = surf_set.get_surfaces()
        surface = trimatic.merge(surfaces)
        surface.name=surf_set.name
    return part

#Get all interface surfaces
NMA = trimatic.find_part('NMA')
if NMA is None:
    stem=trimatic.find_part('stem_NMA')
    cement=trimatic.find_part('cement_NMA')
    shaft=trimatic.find_part('shaft_NMA')
    NMA=trimatic.create_non_manifold_assembly_intersection(shaft, [cement,stem])
    NMA.name = 'NMA'


if len(NMA.find_surface_sets('interface_stem_NMA_cement_NMA')[0].get_surfaces())>1:
    raise KeyboardInterrupt('More then two surfaces in stem cement interface')

interface_surf_sets = NMA.find_surface_sets('.*interface.*')
local_parameters=[]
for surf_set in interface_surf_sets:
    if re.match('.*[Hh]ead.*[Ss]haft.*',surf_set.name):
        continue #This does not need to be meshed smaller
    surfaces = surf_set.get_surfaces()
    for surf in surfaces:
        local_parameters.append((surf, bc.interface_mesh_size, 0.0))

trimatic.adaptive_remesh(entities=NMA, target_triangle_edge_length=bc.mesh_size,
                          preserve_surface_contours=True)
trimatic.adaptive_remesh(entities=NMA, target_triangle_edge_length=bc.mesh_size,
                         preserve_surface_contours=True, local_remesh_parameters=tuple(local_parameters),local_growth_rate=15)
trimatic.adaptive_remesh(entities=NMA, target_triangle_edge_length=bc.mesh_size,
                         preserve_surface_contours=False, local_remesh_parameters=tuple(local_parameters),local_growth_rate=15)




# local_parameters_list.append((tip_surf, k - 1 + corr2, 0.0))
#
# # Remesh NMA
# remeshed_nma = trimatic.adaptive_remesh(entities=nma, target_triangle_edge_length=k-1+corr2,
#                                         preserve_surface_contours=False)
# assert remeshed_nma == True, "Adaptive remesh of NMA failed"
# remeshed_nma = trimatic.adaptive_remesh(entities=nma, target_triangle_edge_length=k,
#                                         preserve_surface_contours=True,
#                                         local_remesh_parameters=tuple(local_parameters_list), local_growth_rate=30)

cement=create_part_with_surf_name(NMA,'Cement')
shaft=create_part_with_surf_name(NMA,'Shaft')
# head=create_part_with_surf_name(NMA,'Head')
stem=create_part_with_surf_name(NMA,'Stem')

# trimatic.create_volume_mesh(cement,maximum_edge_length=6)
# trimatic.create_volume_mesh(shaft,maximum_edge_length=6)
# trimatic.create_volume_mesh(head,maximum_edge_length=6)
# trimatic.create_volume_mesh(stem,maximum_edge_length=6)
