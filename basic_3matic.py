import trimatic
import json
import basic_functions as bf

def write_json(path, parameter_list):
    with open(path, "w") as json_file:
        json_file.write('{\n')
        last_value = False
        for index,parameter in enumerate(parameter_list):
            if index == len(parameter_list) - 1:
                last_value = True
            if type(parameter)==dict:
                write_json_dict(parameter,json_file,last_value)
            else:
                write_json_list(parameter,json_file,last_value)
        json_file.write('}\n')

def write_json_list(parameter, json_file, last_value):
    parameter_name = parameter[0]
    parameter_value = parameter[1]
    string_lst = write_string_lst(parameter_value,parameter_name,json_file)
    for i,string in enumerate(string_lst):
        if last_value and i==len(string_lst)-1:  # Last parameter may not have the ','
            json_file.write(string[:-2]+'\n')
        else:
            json_file.write(string)
    return json_file

def write_string_lst(parameter_value,parameter_name,json_file):
    if type(parameter_value) == trimatic.Point:
        string_lst = write_point_str(parameter_value, parameter_name, json_file)
    elif type(parameter_value) == trimatic.Plane:
        string_lst = write_plane_str(parameter_value, parameter_name, json_file)
    elif type(parameter_value) == str:
        string_lst = write_str_str(parameter_value, parameter_name, json_file)
    else:
        string_lst = write_normal_str(parameter_value, parameter_name, json_file)
    return string_lst

def write_point_str(point, point_name, json_file):
    string = '\t"' + point_name + '": {},\n'.format(list(point.coordinates))
    return [string]

def write_str_str(string, string_name, json_file):
    string = '\t"' + string_name + '": {},\n'.format('"'+string+'"')
    return [string]

def write_plane_str(plane, plane_name, json_file):
    string1 = '\t"Origin ' + plane_name + '": {},\n'.format(list(plane.origin))
    string2 = '\t"Normal ' + plane_name + '": {},\n'.format(list(plane.normal))
    return [string1, string2]


def write_normal_str(parameter_value, parameter_name, json_file):
    string = '\t"' + parameter_name + '": {},\n'.format(list(parameter_value))
    return [string]

def write_json_dict(parameter, json_file,last_value):
    counter=0
    for parameter_name, parameter_value in parameter.items():
        counter+=1
        string_lst = write_string_lst(parameter_value, parameter_name, json_file)
        for i, string in enumerate(string_lst):
            if last_value and i == len(string_lst) - 1 and counter == len(parameter):  # Last parameter may not have the ','
                json_file.write(string[:-2] + '\n')
            else:
                json_file.write(string)
    return json_file

def read_json(path,parameter_strings):
    with open(path) as data_file:
        refs = json.load(data_file)
        ref = list()
        for string in parameter_strings:
            ref.append(refs[string])
    return ref


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

#movement
def translate_direction_and_distance(entities, distance, direction, number_of_copies=0):
    translation_vector = [0, 0, 0]
    for i in range(3):
        translation_vector[i] = direction[i] * distance
    return trimatic.translate(entities, tuple(translation_vector), number_of_copies)

def translate_from_point_to_point(entities, point_from, point_to, number_of_copies=0):
    trimatic.utils.check_license('translate', '3-matic Base')

    translation_vector = [0, 0, 0]
    for i in range(3):
        translation_vector[i] = point_to[i] - point_from[i]
    ##### return trimatic.translate(trimatic.single_or_multiple_entities(entities),trimatic.point_argument(translation_vector),number_of_copies)
    return trimatic.translate((entities), (translation_vector), number_of_copies)

#Creation
def create_points(points,names):
    if type(points)==list: #Create a list of points and names
        points_lst=[]
        for i,point in enumerate(points):
            pt=trimatic.create_point(point)
            pt.name=names[i]
            points_lst.append(pt)
        return points_lst
    else: #create a single point
        pt=trimatic.create_point(points)
        pt.name=names
        return pt

def create_plane_2_points_normal(p1,p2,normal):
    p12 = bf.min(p1,p2)
    normal = bf.cross(p12,normal)
    pl = trimatic.create_plane_normal_origin(normal, list(p1))
    return pl

def clean_up(objects_to_keep):
    objects = list(trimatic.get_objects())
    for o in objects:
        if o in objects_to_keep:
            continue
        try:
            trimatic.delete(o)
        except:
            pass
    return None