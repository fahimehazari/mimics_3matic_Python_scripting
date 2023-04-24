#root_folder_scripts = sys.path[0]
#TODO: should be present automatic (we now install)
#sys.path.append(os.path.join(root_folder_scripts,'..','..','..'))

import basic_configuration as bc
import mimics
import glob
import time

class Prop: pass

#######################################################################################################
###################### Main script ####################################################################
#######################################################################################################
# This script assigns material properties to the femur and implant mesh. The material properties files
# have to be manually created (one for each bone) and placed in the folder "Datasets\Look-up files".

# Set path
root_folder = r"C:\MedData\UZBrussel projects\Mesh creation"
source_folder = os.path.join(root_folder, "Meshed femurs") # contains the volume meshes
source_folder_mcs = os.path.join(root_folder, "Datasets\Mimics") # contains the original mimics files
source_folder_xml = os.path.join(root_folder, "Datasets\Look-up files") # contains the xml look-up files for bone and implant
derived_folder = os.path.join(root_folder, "Meshed femurs with material assignment") # output projects will be placed in this folder
if not os.path.exists(derived_folder):
    os.mkdir(derived_folder)
FEA_folder = os.path.join(root_folder, "FEA preparation")
if not os.path.exists(FEA_folder):
    os.mkdir(FEA_folder)
print("Start material assignment")

# Iterate over all the source 3-matic files
for fldr in glob.glob(os.path.join(source_folder, "*")):
    files = glob.glob(os.path.join(fldr, "*for-import-into-Mimics.mxp"))
    for mxp_file_name in files[0:2]:
    #for mxp_file_name in glob.glob(os.path.join(fldr, "*for-import-into-Mimics.mxp")):
        project_name = os.path.split(mxp_file_name)[1][:-4]
        print(project_name)

# Create subfolder for saving the resulting files
        index_end_bone = project_name.find(" - ")
        index_end_implant = project_name.find((" - "), index_end_bone + 3)
        bone_name = project_name[0:index_end_bone]
        bone_derived_folder = os.path.join(derived_folder, bone_name)
        if not os.path.exists(bone_derived_folder):
            os.mkdir(bone_derived_folder)
        bone_FEA_folder = os.path.join(FEA_folder, bone_name)
        if not os.path.exists(bone_FEA_folder):
            os.mkdir(bone_FEA_folder)

# Import files
        mcs_file_name = os.path.join(source_folder_mcs, project_name + ".mcs")
        mimics.dialogs.set_predefined_answer(mimics.dialogs.dialog_id.CONTINUE_WITH_OUTDATED_DATA_MODEL,
                                             mimics.dialogs.answer.Yes)
        mimics.file.open_project(mcs_file_name)
        mimics.file.import_3matic_project(mxp_file_name)
        lookup_file_implant = os.path.join(source_folder_xml,"Implant.xml")
        lookup_file_femur = os.path.join(source_folder_xml, bone_name + " - Bone material properties.xml")

# Find parts
        implant = mimics.data.meshes.find("Implant")
        femur_shaft = mimics.data.meshes.find("Femur_shaft")
        femur_head = mimics.data.meshes.find("Femur_head")

# INTACT FEMUR
# Assign materials
        mimics.fea.assign_material_from_lookup(femur_shaft, lookup_file_femur)
        mimics.fea.assign_material_from_lookup(femur_head, lookup_file_femur)
        mimics.fea.assign_material_from_lookup(implant, lookup_file_femur)

# Export mesh
        implant_name_and_size = project_name[index_end_bone + 3:index_end_bone + 14]
        if implant_name_and_size[-1] == " ":
            index_end_implantsize = index_end_bone + 13
        else:
            index_end_implantsize = index_end_bone + 14
        if bc.position_variation_mode == False:
            new_project_name = project_name[0:8] + " - " + project_name[index_end_bone + 3:index_end_implantsize]
        else:
            new_project_name = project_name[0:8] + " - " + project_name[index_end_bone + 3:index_end_implantsize] + " - " \
                               + project_name[index_end_implant + 3:-25] + " - "
        inp_filename = os.path.join(bone_FEA_folder, new_project_name + " - Intact - Mesh-archive-Volume.inp")
        if os.path.exists(inp_filename):
            os.remove(inp_filename)  # delete file if it already exists
        mimics.file.export_mesh_to_abaqus_as_single_output([femur_shaft, implant, femur_head], inp_filename, create_assembly=True,
                                         export_surfaces=False, export_volumes=True, element_type="C3D4")
        inp_filename_surface = os.path.join(bone_FEA_folder, new_project_name + " - Intact - Mesh-archive-Surface.inp")
        if os.path.exists(inp_filename_surface):
            os.remove(inp_filename_surface)  # delete file if it already exists
        mimics.file.export_mesh_to_abaqus_as_single_output([femur_shaft, implant, femur_head], inp_filename_surface, create_assembly=True,
                                                          export_surfaces=True, export_volumes=False, element_type="C3D4")

        mcs_output_file = os.path.join(bone_derived_folder, project_name[:-25] + " - Intact.mcs")
        if os.path.exists(mcs_output_file):
            os.remove(mcs_output_file)  # delete file if it already exists
        mimics.file.save_project(mcs_output_file)

# IMPLANTED FEMUR
# Assign materials
        mimics.fea.assign_material_from_lookup(implant, lookup_file_implant)

# Export mesh
        implant_name_and_size = project_name[index_end_bone + 3:index_end_bone + 14]
        if implant_name_and_size[-1] == " ":
            index_end_implantsize = index_end_bone + 13
        else:
            index_end_implantsize = index_end_bone + 14
        if bc.position_variation_mode == False:
            new_project_name = project_name[0:8] + " - " + project_name[index_end_bone + 3:index_end_implantsize]
        else:
            new_project_name = project_name[0:8] + " - " + project_name[index_end_bone + 3:index_end_implantsize] + " - " \
                               + project_name[index_end_implant + 3:-25] + " - "
        inp_filename = os.path.join(bone_FEA_folder, new_project_name + " - Implanted - Mesh-archive-Volume.inp")
        if os.path.exists(inp_filename):
            os.remove(inp_filename)  # delete file if it already exists
        mimics.file.export_mesh_to_abaqus_as_single_output([femur_shaft, implant], inp_filename, create_assembly=True,
                                         export_surfaces=False, export_volumes=True, element_type="C3D4")
        inp_filename_surface = os.path.join(bone_FEA_folder, new_project_name + " - Implanted - Mesh-archive-Surface.inp")
        if os.path.exists(inp_filename_surface):
            os.remove(inp_filename_surface)  # delete file if it already exists
        mimics.file.export_mesh_to_abaqus_as_single_output([femur_shaft, implant], inp_filename_surface, create_assembly=True,
                                                          export_surfaces=True, export_volumes=False, element_type="C3D4")

        mcs_output_file = os.path.join(bone_derived_folder, project_name[:-25] + " - Implanted.mcs")
        if os.path.exists(mcs_output_file):
            os.remove(mcs_output_file)  # delete file if it already exists
        mimics.file.save_project(mcs_output_file)

print("Done")

