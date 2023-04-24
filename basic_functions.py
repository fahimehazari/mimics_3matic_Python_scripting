import re
import os
import math
import glob
import json
import numpy as np
import basic_configuration as bc
import logger
from collections import OrderedDict


# Directory organisation functions
def join_path(base,new_string):
    return base+'/'+new_string

def check_existence(Folder):
    """Check's the existence of a folder and creates it if it doesn't exist."""
    if not os.path.exists(Folder):
        os.mkdir(Folder)  # if the folder does not yet exist, the folder is created


def clear_folder(Folder):
    """Empties a folder from all mxp and mcs files inside of it."""
    filetypes_list = ["*.stl", "*.mxp"]
    for filetype in filetypes_list:
        dicom_file = join_path(Folder, filetype)
        dicom_file = sorted(
            glob.glob(dicom_file))  # return a possibly-empty list of path names that match 'mxp_source_file'
        for file in dicom_file:
            os.remove(file)


def get_files_with_extension(Folder, filetypes_list):
    """Retrieves all files with a certain extension in a certain folder"""
    all_files = []
    for filetype in filetypes_list:
        files = join_path(Folder, filetype)
        files = sorted(glob.glob(files))  # return a possibly-empty list of path names that match 'mxp_source_file'
        for file in files:
            all_files.append(file)
    return all_files


def clear_folder_completely(Folder):
    """Empties a folder from all mxp and mcs files inside of it."""
    files = get_files_with_extension(Folder, filetypes_list=['*.*'])
    for file in files:
        os.remove(file)


def create_empty_folder(folder):
    """Creates a clean folder"""
    check_existence(folder)
    clear_folder_completely(folder)


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)  # delete file if it already exists


def find_bone_and_implant_name(project_name):
    index_begin_bone = project_name.find("-") + 1
    index_begin_implant = project_name.find((" - "), index_begin_bone) + 3
    bone_name = project_name[index_begin_bone:project_name.find('_', index_begin_bone + 2)]
    index_end_implant = len(project_name)  # project_name.find('.', index_begin_implant + 14)
    implant_name = project_name[
                   index_begin_implant:index_end_implant]  # project_name.find('.', indexBeginImplant + 9)+3
    return bone_name, implant_name, [index_begin_bone, index_begin_implant, index_end_implant]


def write_json(path, parameter_list):
    with open(path, "w") as json_file:
        json_file.write('{\n')
        last_value = False
        for index, parameter in enumerate(parameter_list):
            if index == len(parameter_list) - 1:
                last_value = True
            if type(parameter) == dict:
                write_json_dict(parameter, json_file, last_value)
            else:
                write_json_list(parameter, json_file, last_value)
        json_file.write('}\n')


def write_json_list(parameter, json_file, last_value):
    parameter_name = parameter[0]
    parameter_value = parameter[1]
    string_lst = write_string_lst(parameter_value, parameter_name, json_file)
    for i, string in enumerate(string_lst):
        if last_value and i == len(string_lst) - 1:  # Last parameter may not have the ','
            json_file.write(string[:-2] + '\n')
        else:
            json_file.write(string)
    return json_file


def write_string_lst(parameter_value, parameter_name, json_file):
    if type(parameter_value) == str:
        string_lst = write_str_str(parameter_value, parameter_name, json_file)
    else:
        string_lst = write_normal_str(parameter_value, parameter_name, json_file)
    return string_lst


def write_str_str(string, string_name, json_file):
    string = '\t"' + string_name + '": {},\n'.format('"' + string + '"')
    return [string]


def write_normal_str(parameter_value, parameter_name, json_file):
    try:
        string = '\t"' + parameter_name + '": {},\n'.format(list(parameter_value))
    except TypeError:  # It's not an iterable
        string = '\t"' + parameter_name + '": {},\n'.format([parameter_value])
    return [string]


def write_json_dict(parameter, json_file, last_value):
    counter = 0
    for parameter_name, parameter_value in parameter.items():
        counter += 1
        string_lst = write_string_lst(parameter_value, parameter_name, json_file)
        for i, string in enumerate(string_lst):
            if last_value and i == len(string_lst) - 1 and counter == len(
                    parameter):  # Last parameter may not have the ','
                json_file.write(string[:-2] + '\n')
            else:
                json_file.write(string)
    return json_file


##Store the points
def write_np_arr_json(pts_arr, path):
    one_list = create_one_list(pts_arr)
    delete_file(path)
    write_json(path, parameter_list=one_list)


def create_one_list(pts_arr):
    one_list = []
    for row in range(0, len(pts_arr)):
        for column in range(0, len(pts_arr[0])):
            string = 'r' + str(row) + 'c' + str(column)
            try:
                one_list.append((string, tuple(pts_arr[row][column])))
            except TypeError:  # If it's not coordinate (thus a list) but an int (or numpy float) then you can't convert it to a tuple
                one_list.append((string, (pts_arr[row][column])))
    return one_list


def arr_to_one_list(arr):
    '''Transforms a nested array to one long list'''
    new_list = []
    for row in range(0, len(arr)):
        for col in range(0, len(arr[0])):
            new_list.append(arr[row][col])
    return new_list


def read_json(path, parameter_strings):
    with open(path) as data_file:
        refs = json.load(data_file)
        ref = list()
        for string in parameter_strings:
            ref.append(refs[string])
    return ref


def read_json_as_dict(path):
    with open(path) as data_file:
        refs = json.load(data_file)
    return refs


def create_paths(one_sub_folder=False):
    root_folder = bc.root_path
    mcs_folder = join_path(root_folder,
                              "0 mimics surface")  # the files to be segmented are placed in this folder
    check_existence(mcs_folder)
    results_folder = join_path(root_folder,
                                  "results")  # the files to be segmented are placed in this folder
    assert os.path.exists(results_folder)
    reference_folder = join_path(root_folder,
                                    "1 reference data")  # the files to be segmented are placed in this folder
    check_existence(reference_folder)
    sub_folders = glob.glob(join_path(results_folder, "*"))

    if one_sub_folder:
        return sub_folders[0]

    return root_folder, mcs_folder, results_folder, reference_folder, sub_folders


def create_dicts(amount):
    lst = []
    for i in range(0, amount):
        lst.append({})
    return lst


def remove_duplicates(lst):
    '''Removes duplicates and maintains the order'''
    return list(OrderedDict.fromkeys(lst))


def is_implanted_femur(file_name):
    if re.match('.*implanted.*', file_name) is None:
        return False
    return True


def get_file_by_keyword(path, keyword, multiple=False):
    '''Returns one file if multiple is falls returns a list of files if true'''
    if multiple:
        searched_file = []
    for file in glob.glob(join_path(path, "*")):
        if re.match('.*' + keyword + '.*', file) != None:
            if not multiple:
                searched_file = file
                break
            else:
                searched_file.append(file)
    return searched_file


# Basic math
def plus(u, v):
    return [u[i] + v[i] for i in range(len(u))]


def mul(u, k):
    return [u[i] * k for i in range(len(u))]


def min(u, v):
    return [u[i] - v[i] for i in range(len(u))]


def dot(u, v):
    return sum(u[i] * v[i] for i in range(len(u)))


def cross(a, b):
    assert len(a) == len(b) == 3, 'For 3D vectors only'
    a1, a2, a3 = a
    b1, b2, b3 = b
    return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1]


def magnitude(v):
    total = 0
    for i in range(len(v)):
        total += v[i] ** 2
    return math.sqrt(total)


# def magnitude(v): #Slow for abaqus which is so old that it uses python 2.7
#     return math.sqrt(sum(v[i] * v[i] for i in range(len(v))))

def normalize(v):
    return [i / magnitude(v) for i in v]


def distance(u, v):
    d = 0
    for i in range(len(u)):
        dc = u[i] - v[i]
        d += dc * dc
    return math.sqrt(d)


# Advanced math
# found on http://stackoverflow.com/questions/9605556/how-to-project-a-3d-point-to-a-3d-plane
def point_to_plane_projection(pt, origin, normal):
    ap = min(pt, origin)
    dp = dot(ap, normal) / dot(normal, normal)
    return plus(pt, mul(normal, -dp))


def point_to_line_projection(pt, origin, direction):
    ap = min(pt, origin)
    dp = dot(ap, direction) / dot(direction, direction)
    return plus(origin, mul(direction, dp))


def point_to_1D_projection(pt, origin, direction):
    '''Returns coordinates of the pt on the 1D axis'''
    proj_pt = point_to_line_projection(pt, origin, direction)
    dist = distance(origin, proj_pt)
    if dot(min(proj_pt, origin), direction) < 0:
        sign = -1
    else:
        sign = 1
    return dist * sign


# found on http://stackoverflow.com/questions/5188561/signed-angle-between-two-3d-vectors-with-same-origin-within-the-same-plane
# this function calculates an angle between two lines, but also assigns a sign to the angle
def angle_signed_on_plane(v1, v2, normal, epsilon=1e-6, signed=True):
    cross_p = cross(v1, v2)
    sinang = magnitude(cross_p)
    cosang = dot(v1, v2)
    if sinang < epsilon and cosang > 1 - epsilon:  # This is zero degrees
        return 0.0
    elif sinang < epsilon and cosang < -1 + epsilon:  # This is plus or minus 180 degrees
        return 180.0
    angle = math.atan2(sinang, cosang)
    if dot(normal, cross_p) < 0:  # Extra parameter signed allows to make it signed or not
        angle = -angle
    if angle < 0 and signed == False:  # Only give positive angles
        return 360 + math.degrees(angle)
    return math.degrees(angle)


def line_plane_intersection(p0, p1, p_co, p_no, epsilon=1e-6):
    """
    p0, p1: define the line
    p_co, p_no: define the plane:
        p_co is a point on the plane (plane coordinate).
        p_no is a normal vector defining the plane direction; does not need to be normalized.

    return a Vector or None (when the intersection can't be found).
    """

    u = min(p1, p0)
    dotp = dot(p_no, u)

    if math.fabs(dotp) > epsilon:
        # the factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = min(p0, p_co)
        fac = -dot(p_no, w) / dotp
        u = mul(u, fac)
        return plus(p0, u)
    else:
        # The segment is parallel to plane
        return None


# found on: https://www.learnopencv.com/rotation-matrix-to-euler-angles/
# Checks if a matrix is a valid rotation matrix.
def is_rotation_matrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


# found on: https://www.learnopencv.com/rotation-matrix-to-euler-angles/
# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotation_matrix_to_euler_angles(R):
    assert (is_rotation_matrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([math.degrees(x), math.degrees(y), math.degrees(z)])


def is_on_normal_side_of_plane(pt, origin, normal):
    '''Checks if a point is on the same side as the normal of the plane is pointing to'''
    proj_pt = point_to_plane_projection(pt, origin, normal)
    direction = normalize(min(pt, proj_pt))
    if dot(direction, normal) < 0:
        return False
    return True


def line_circle_intersection_pt(center, radius, pt1, pt2):
    '''Explanation at: https://codereview.stackexchange.com/questions/86421/line-segment-to-circle-collision-algorithm?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    (Also works for 3D)'''
    line = min(pt2, pt1)  # Vector along line segment

    a = dot(line, line)
    b = 2 * dot(line, min(pt1, center))
    c = dot(pt1, pt1) + dot(center, center) - 2 * dot(pt1, center) - radius ** 2

    disc = b ** 2 - 4 * a * c
    if disc < 0:
        return False, None

    sqrt_disc = math.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    if (0 <= t1 <= 1):
        return plus(pt1, mul(line, t1))
    if 0 <= t2 <= 1:
        return plus(pt1, mul(line, t2))
    else:
        return None


# List organizing
def find_closest_point(point, points_list):
    """Find the closest point in a list to a certain point"""
    min_distance = 10000  # Taking a super large distance so it's certainly not the smallest
    ind = 0
    for pt in points_list:
        dist_betw_pts = distance(point, pt)
        if dist_betw_pts < min_distance:
            min_point = pt
            min_distance = dist_betw_pts
            min_ind = ind
        ind = ind + 1
    return min_point, min_ind


def from_2d_to_3d(pt):
    pt_lst = [pt[0], pt[1], 0]  # zero is added for 3D
    return pt_lst


def sort_list_with_index_output(lst):
    '''sorts a list by value, but returns the indexes at the corresponding places'''
    return sorted(range(len(lst)), key=lambda k: lst[k])


##Trivia
def keys(dict):
    return list(dict.keys())


# Interpolation
def find_value_corr_to_por(value_corr_to_por_dict, por, original_value):
    '''Finds a value as a function of the porosity'''
    for key in value_corr_to_por_dict:
        if key != 'porosity':
            value_key = key

    porosity_increments = value_corr_to_por_dict['porosity']
    value_increments = value_corr_to_por_dict[value_key]

    # Check if None, than it's an element above the line of interest
    if por >= 1 and por < 1.005:
        return (original_value, por)

    # Find the correct index
    index = find_por_index(porosity_increments, por)

    # Interpolate between two neighbouring values
    value = interpolate_2_values(index, por, porosity_increments, value_increments)

    return (value * original_value, por)


def find_por_index(porosity_increments, por):
    for i, por_increment in enumerate(porosity_increments):
        if por_increment >= por:
            index = i - 1
            break
    return index


def interpolate_2_values(index, por, porosity_increments, value_increments):
    dist1 = por - porosity_increments[index]
    dist2 = porosity_increments[index + 1] - por
    tot = dist1 + dist2
    value = dist2 / tot * value_increments[index] + dist1 / tot * value_increments[index + 1]
    return value


# Create logger
def create_logger(script_title='None', sub_folder=1, last_sub_folder=0):
    log = logger.Logger(sub_folder)
    if sub_folder != last_sub_folder:
        log.script_title(script_title)
    return log


# Classes
class Plane:
    def __init__(self, origin, normal):
        self.origin = origin
        self.normal = normal
        self.object_coordinate_system = self.get_coo_sys()
        self.x_axis = self.object_coordinate_system[0]
        self.y_axis = self.object_coordinate_system[1]
        self.z_axis = self.object_coordinate_system[2]

    def get_coo_sys(self):
        perp_vect_3 = self.normal
        in_plane_vect = [1, 0, 0]
        if dot(perp_vect_3, in_plane_vect) == 1:  # This is exactly the same vector take another one
            in_plane_vect = [0, 1, 0]
        in_plane_vect = point_to_plane_projection(in_plane_vect, self.origin, self.normal)
        perp_vect_1 = normalize(in_plane_vect)  # Now we have a perpendicular vector in the plane
        perp_vect_2 = normalize(cross(perp_vect_3, perp_vect_1))
        return [perp_vect_1, perp_vect_2, perp_vect_3]


class CooSys():
    def __init__(self, origin=(0, 0, 0), x_axis=(1, 0, 0), y_axis=(0, 1, 0), z_axis=(0, 0, 1)):
        self.origin = origin
        self.x_axis = normalize(x_axis)
        self.y_axis = normalize(y_axis)
        self.z_axis = normalize(z_axis)
        self.rotation_matrix = np.array([self.x_axis, self.y_axis,
                                         self.z_axis])  # Rotation matrix to go to this coo_sys from world
