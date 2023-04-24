import trimatic

#Find parts
cut_pl=trimatic.find_planes('[Cc]ut.*')[0]
bone_p=trimatic.find_parts('[Ff]emur.*')[0]
stem_p=trimatic.find_parts('[Ss]tem.*')[0]
cement_p=trimatic.find_parts('[Cc]ement.*')[0]

#Remesh this stuff
# femur
remeshed_femur = trimatic.duplicate(bone_p)
remeshed_implant = trimatic.duplicate(stem_p)
remeshed_cement = trimatic.duplicate(cement_p)

trimatic.adaptive_remesh(entities=remeshed_femur, target_triangle_edge_length=1,
                         preserve_surface_contours=False)
remeshed_femur = trimatic.uniform_remesh(entities=remeshed_femur, target_triangle_edge_length=1)

trimatic.adaptive_remesh(entities=remeshed_cement, target_triangle_edge_length=1,
                         preserve_surface_contours=False)
remeshed_cement = trimatic.uniform_remesh(entities=remeshed_cement, target_triangle_edge_length=1)

# implant
trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=1,
                         preserve_surface_contours=False)
remeshed_implant = trimatic.uniform_remesh(entities=remeshed_implant, target_triangle_edge_length=1)
# trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=1,
#                          preserve_surface_contours=True)
# trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=1,
#                          preserve_surface_contours=True)
# trimatic.fix.smooth(remeshed_implant, 0.3)
# trimatic.adaptive_remesh(entities=remeshed_implant, target_triangle_edge_length=1,
#                          preserve_surface_contours=True)


#fix the mesh
trimatic.fix.auto_fix(entities=remeshed_femur)
trimatic.fix.auto_fix(entities=remeshed_implant)
trimatic.fix.auto_fix(entities=remeshed_cement)
remeshed_femur.name='remeshed femur'
remeshed_implant.name='stem_NMA'
remeshed_cement.name='cement_NMA'

#Cut the head
cut_parts = trimatic.cut(remeshed_femur, cut_pl)
if cut_parts[0].volume > cut_parts[1].volume:
    femur_head = cut_parts[1]
    femur_shaft = cut_parts[0]
else:
    femur_head = cut_parts[0]
    femur_shaft = cut_parts[1]

femur_head.name = 'Head Final'
femur_shaft.name = 'shaft_NMA'


#Remesh stem and head
trimatic.adaptive_remesh(entities=[remeshed_implant,remeshed_cement,femur_head,femur_shaft], target_triangle_edge_length=2,
                         preserve_surface_contours=False)
trimatic.adaptive_remesh(entities=[remeshed_implant,remeshed_cement,femur_head,femur_shaft], target_triangle_edge_length=2,
                         preserve_surface_contours=False)

# #Create NMA
# cement_stem_NMA=trimatic.create_non_manifold_assembly_intersection(remeshed_cement, [remeshed_stem])

# #Find parts
# femur_head=trimatic.find_parts('[Hh]ead.*')[0]
# femur_shaft=trimatic.find_parts('[Ss]haft.*')[0]
# [femur_head,femur_shaft]=trimatic.duplicate([femur_head,femur_shaft])
# femur_shaft.name = 'Shaft'
# femur_head.name = 'Head'
# remeshed_cement=trimatic.find_parts('remeshed cement')[0]
# remeshed_stem=trimatic.find_parts('remeshed stem')[0]
#
# #Create an NMA of cement_and_stem
# [remeshed_stem,remeshed_cement]=trimatic.duplicate([remeshed_stem,remeshed_cement])
# remeshed_cement.name = 'remeshed cement'
# remeshed_stem.name = 'remeshed stem'
# cement_stem_NMA=trimatic.create_non_manifold_assembly_intersection(remeshed_cement, [remeshed_stem])
# cement_stem_NMA.name = 'Cement stem NMA'
# trimatic.adaptive_remesh(entities=cement_stem_NMA, target_triangle_edge_length=1,
#                          preserve_surface_contours=False)
# trimatic.adaptive_remesh(entities=cement_stem_NMA, target_triangle_edge_length=1,
#                          preserve_surface_contours=False)
# interface_cement_stem = cement_stem_NMA.find_surface_sets('.*[Cc]ement.*')[0]
# surface_lst=interface_cement_stem.find_surfaces('.*')
# print(surface_lst)
#
# if len(surface_lst)>1: #Delete other surfaces in case more then one
#     prev_area=0
#     for surf in surface_lst:
#         if prev_area<surf.area:
#             final_surf=surf
#             prev_area = surf.area
#     for surf in surface_lst:
#         if surf!=final_surf:
#             trimatic.delete(surf)
#
# #Create a copy without the interface
# cement_stem_NMA_d = trimatic.duplicate(cement_stem_NMA)
# interface_cement_stem_d = cement_stem_NMA_d.find_surface_sets('.*[Ii]nterface.*')[0]
# trimatic.delete(interface_cement_stem_d)
# err
# #Combine the shaft, head and cement_stem_NMA without interface
# NMA = trimatic.create_non_manifold_assembly_intersection(femur_shaft, [femur_head,cement_stem_NMA_d])
# assert NMA is not None
# print('Add the cement_stem interface and do 3 adaptive remeshes')
# print('Split all surfaces to the correct parts and try to fix them')





