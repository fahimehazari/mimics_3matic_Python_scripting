import os
import numpy as np
import basic_functions as bf
import re
import abaqus_help_functions as ahf

''''This script has as objective to add the non-linear material properties to the elements'''
# Find inp-files
source = r'C:\Users\r0732105\Desktop\My Files\Mathys_2\Original CT Data\Mimics\Input files'
bones = ['1L','1R','2L','2R','3L','3R','4L','4R']
bones = ['1L']  # input("What bone do you need? Answer like '2L'")
for bone in bones:
    all_folders = bf.find_all_sub_folders(source)
    for folder in all_folders:
        if re.match('.*' + bone + '.*', folder) is not None:
            break
    all_files = bf.get_files_with_extension(folder, ['*.inp'])

    # Iterate over all inp files
    for inp_file in all_files:
        if re.match('.*tetmesh.*',inp_file):
            os.remove(inp_file)
            continue
        volume_inputlist = ahf.readFile(inp_file)
        new_inputlist = list(volume_inputlist)

        implanted = False
        if re.match('.*implanted.*', inp_file) is not None:
            implanted = True

        # Define material properties
        line_density = ahf.getLineNumberFrom("End Assembly", new_inputlist, 0)
        if implanted:
            density = np.asarray(ahf.readDensity(new_inputlist, line_density, leave_out=10))
        else:
            density = np.asarray(ahf.readDensity(new_inputlist, line_density, 0))

        ash_density = density
        trabecular = np.where(ash_density < 0.28505)
        smaller_than_zero = np.where(ash_density <= 0.05)  # Prevent negative density
        for i in smaller_than_zero:
            ash_density[i] = 0.05

        bigger_than_max = np.where(ash_density >= 1.3)  # Prevent artefacts
        for i in bigger_than_max:
            ash_density[i] = 1.3

            #bigger_than_max = np.where(ash_density >= 1.17)  # Prevent artefacts
            #for i in bigger_than_max:
                #ash_density[i] = 1.17

        E = 14900 * ash_density ** 1.86  # Define youngs modulus
        S = 102 * ash_density ** 1.8  # Define yield stress

        eps_AB_trab = (0.00189 * np.ones(ash_density.shape) + 0.0241 * ash_density) * 15 / 3  # Calculate epsilons
        eps_AB = (0.0184 * np.ones(ash_density.shape) - 0.0100 * ash_density) * 5 / 3
        eps_AB[trabecular] = eps_AB_trab[trabecular]  # Input trabecular values on every place where bone is trabecular bone
        eps_smaller_than_zero = np.where(eps_AB <= 0)
        for i in eps_smaller_than_zero: #If eps AB is smaller than wero make it immediately plastic by giving low eps AB
            eps_AB[i] = 0.0001
        Ep_trab = -2080 * ash_density ** 1.45
        Ep_trab = 3 * E * Ep_trab / (15 * E - (15 - 3) * Ep_trab)
        Ep = -1000
        Ep = 3 * E * Ep / (5 * E - (5 - 3) * Ep)
        Ep[trabecular] = Ep_trab[trabecular]
        sigma_min = 43.1 * ash_density ** 1.81
        eps_final = eps_AB - (S - sigma_min) / Ep + (S - sigma_min) / E #it is minus because Ep is negative

        # Add the nonlinear material properties to the inp-file
        write_line = ahf.getLineNumberFrom("DENSITY", new_inputlist, line_density) + 2
        for i in range(0, len(density)):
            elastic_prop = str(E[i]) + ", 0.3\n"
            plastic_prop = str(S[i]) + ", 0\n" + str(S[i]) + ", " + str(eps_AB[i]) + "\n" + str(
                sigma_min[i]) + ", " + str(
                eps_final[i]) + "\n"
            string_material = "*ELASTIC\n" + elastic_prop + "*PLASTIC\n" + plastic_prop
            new_inputlist.insert(write_line, string_material)
            write_line = write_line + 4

        # Create new inp-file
        new_inp_file = os.path.join(source, inp_file[:-4] + "-tetmesh.inp")
        if os.path.exists(new_inp_file):
            os.remove(new_inp_file)
        ahf.generateFile(new_inputlist, new_inp_file)
