import json
from .filename_reader import create_filename_dict, remove_extension, generate_new_path, is_derivative
import os

def save_file_infos(input_files, participants_dict, out_path, **kwargs):
    """
    Saves a json in `out_path` containing information and sorting instructions ("new_path") for all files in `input_files`

    Kwargs can be used to pre-determine some information

    Parameters
    --------
        input_files : list(str),
            a list of path strings
        participants_dict : dict,
            new sub name given to the former one (e.g. participants_dict['REEVOID_PILOT_01'] = 'sub-pilot')
        out_path : str,
            the path where the file infos will be saved (usually of the type `/file_infos/subdir/file_infos-[n].json`)
    
    Saves
    --------
        out_path, json file
            information about a file can be found as follows: out_path_dict[file]['new_path'] or out_path_dict[file]['type'] etc.

    Kwargs
    --------
        sub : str,
            precises the sub name
        type : str,
            precises if it is 'anat', 'func', etc.
        category : str,
            additional information
        seg_info : str,
            possible information if it is segmentation (zone targeted, mask, ...)
        is_localizer : Bool,
        is_other : Bool,
        is_a_previous_version : Bool,
        is_derivative : Bool,
    """
    final_data= {}
    for file in input_files:
        #print(file)
        final_data[file] = create_filename_dict(file, participants_dict, **kwargs)
    print('done')

    try:
        dirs = '/'.join(out_path.split('/')[:-1])
        os.makedirs(dirs, exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump(final_data, f, indent=4)
    except:
        with open(out_path, 'w') as f:
            json.dump(final_data, f, indent=4)

def refresh_new_paths(file_infos_path, new_file_infos_path):
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
    new_file_infos = file_infos.copy()
    for file in file_infos.keys():
        #print(file_infos[file].keys()) # to debug
        try:
            seg_info = file_infos[file]['seg_info']
        except KeyError:
            seg_info = ''
        new_path = generate_new_path(
            old_path= file_infos[file]['old_path'],
            sub = file_infos[file]['sub'],
            id = file_infos[file]['id'],
            type = file_infos[file]['id'],
            category = file_infos[file]['category'],
            seg_info = seg_info,
            suffix = file_infos[file]['suffix'],
            extension = file_infos[file]['extension'],
            is_tmp_bool = file_infos[file]['is_tmp'],
            is_derivative_bool = is_derivative(file_infos[file]['type']),
            is_localizer_bool = file_infos[file]['is_localizer'],
            is_other_bool = file_infos[file]['is_other'],
            is_a_previous_version_bool = file_infos[file]['is_a_previous_version']
        )
        new_file_infos[file]['new_path'] = new_path
    
    with open(new_file_infos_path, 'w') as f:
        json.dump(new_file_infos, f, indent=4)


def save_jsons_to_data(file_infos_path, jsons_to_data_path):
    """
    Saves a json in `jsons_to_data_path` matching metadata files with their respective data


    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        jsons_to_data_path : str,
            the path where the matches will be saved (usually of the type `/file_infos/subdir/jsons_to_data-[n].json`)
    
    Saves
    --------
        jsons_to_data_path, json file
            metadata-data connections can be found as follows: jsons_to_data_path_dict[json_file] = list(possible matching data files)

    """
    jsons_dict = {}

    data_dict = {}

    out_dict = {}

    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
        all_files = file_infos.keys()
        for file in all_files:
            if file_infos[file]['extension'] == '.json':
                jsons_dict[file] = file_infos[file]
            else:
                data_dict[file] = file_infos[file]

    for json_file in jsons_dict.keys():
        json_filename = json_file.split('/')[-1][:-len('.json')]
        out_dict[json_file] = []
        for data_file in data_dict.keys():
            filename = data_file.split('/')[-1]
            if json_filename in filename:
                out_dict[json_file].append(data_file)

    with open(jsons_to_data_path, 'w') as f:
        json.dump(out_dict, f, indent=4)


def correct_file_infos_with_matching_metadata(file_infos_path, jsons_to_data_path, corrected_file_infos_path):
    """
    Saves a json in `corrected_file_infos_path` correcting the metadata file infos

    If no correction is required, it will save a renamed copy of the initial file


    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        jsons_to_data_path : str,
            path to metadata-data matching file
        corrected_file_infos_path : str,
            the path where the corrected file infos will be saved (usually of the type `/file_infos/subdir/file_infos-[n]_corrected.json`)
    
    Saves
    --------
        corrected_file_infos_path, json file
            information about a file can be found as follows: corrected_file_infos_path_dict[file]['new_path'] or corrected_file_infos_path_dict[file]['type'] etc.
    """
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)

    with open(jsons_to_data_path, 'r') as f:
        jsons_to_data = json.load(f)

    for json_file in jsons_to_data.keys():
        assert len(jsons_to_data[json_file])<=1
        if len(jsons_to_data[json_file])==1:
            matching_file = jsons_to_data[json_file][0]
            json_file_infos = file_infos[matching_file].copy()
            json_file_infos['extension'] = '.json'
            json_file_infos['old_path'] = file_infos[json_file]['old_path']
            data_new_path = json_file_infos['new_path']
            json_new_path = remove_extension(data_new_path) + '.json'

            json_file_infos['new_path'] = json_new_path
            file_infos[json_file] = json_file_infos

    with open(corrected_file_infos_path, 'w') as f:
        json.dump(file_infos, f, indent=4)



def write_paths_file(file_infos_path, out_path, old_prefix='', new_prefix=''):
    """
    Saves a txt in `out_path` logging the sorting instructions in `file_infos_path`, where each line is of the sort ~/old/path/to/file, ~/new/path/to/file

    Prefixes can be specified to be added before the old and new paths

    **Overwrites the file in `out_path`**

    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        out_path : str,
            path to where the logs will be saved (must end in .txt), usually of the type `/paths/subdir/paths-[n].txt`
        old_prefix = '' : str,
            the prefix that will be added to the left hand paths in the file, redundant dashes will be corrected
        new_prefix = '' : str,
            the prefix that will be added to the right hand paths in the file, redundant dashes will be corrected
    
    Saves
    --------
        out_path, txt file
            logs of the changes proposed in `file_infos_path`

            each line is of the sort: ~/old/path/to/file, ~/new/path/to/file
    """
    with open(file_infos_path,'r') as f:
        data = json.load(f)
    
    out_dirs = '/'.join(out_path.split('/')[:-1])
    corrected_old_prefix = old_prefix
    corrected_new_prefix = new_prefix
    if old_prefix != '':
        if corrected_old_prefix[-1]=='/':
            corrected_old_prefix = corrected_old_prefix[:-1]
        if corrected_old_prefix[0] != '/':
            corrected_old_prefix = '/' + corrected_old_prefix
    if new_prefix != '':
        if corrected_new_prefix[-1]!='/':
            corrected_new_prefix +='/'
        if corrected_new_prefix[0] =='/':
            corrected_new_prefix = corrected_new_prefix[1:]
    
    try:
        os.makedirs(out_dirs)
        with open(out_path,'w') as f:
            for file in data.keys():
                f.write('~' + corrected_old_prefix + data[file]['old_path'] + ', ~/' + corrected_new_prefix + data[file]['new_path'])
                f.write('\n')
    except:
        with open(out_path,'w') as f:
            for file in data.keys():
                f.write('~' + corrected_old_prefix + data[file]['old_path'] + ', ~/' + corrected_new_prefix + data[file]['new_path'])
                f.write('\n')


def write_general_recap_file(file_infos_path, out_path, new_prefix=''):
    """
    Saves a json in `out_path` listing the types of data available for each sub: `out_path_dict[sub][type]` is a list of the new paths of the data on the specified type and sub

    Prefixes can be specified to be added before the new paths

    **Overwrites the file in `out_path`**

    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        out_path : str,
            path to where the recap will be saved (must end in .json), usually of the type `/recaps/subdir/recap-[n].json`
        new_prefix = '' : str,
            the prefix that will be added to the right hand paths in the file
    
    Saves
    --------
        out_path, json file
            recap of the available data for each sub
    """
    with open(file_infos_path,'r') as f:
        file_infos = json.load(f)
    
    out_dirs = '/'.join(out_path.split('/')[:-1])
    out_data = {}

    os.makedirs(out_dirs, exist_ok=True)

    with open(out_path,'w') as f:
        for file in file_infos.keys():
            type = file_infos[file]['type']
            new_path = new_prefix + file_infos[file]['new_path']
            is_tmp_bool = file_infos[file]['is_tmp']
            sub = file_infos[file]['sub']
            if not is_tmp_bool:
                if sub not in out_data.keys():
                    out_data[sub] = {}
                elif type in out_data[sub].keys():
                    out_data[sub][type].append(new_path)
                else:
                    out_data[sub][type] = [new_path]
        json.dump(out_data, f, indent=4)
        

def merge_general_recaps(input_files, out_path):
    """
    Merges the json recaps listed in `input_files` and saves the result in `out_path`

    **Overwrites the file in `out_path`**

    Parameters
    --------
        input_file : list(str),
            list of paths to json recaps to be merged
        out_path : str,
            path to where the merged recap will be saved (must end in .json)
   
    Saves
    --------
        out_path, json file
            merged recap of the available data for each sub
    """
    out_data = {}
    for file in input_files:
        with open(file, 'r') as f:
            file_data = json.load(f)
        for sub in file_data.keys():
            if sub not in out_data.keys():
                out_data[sub] = file_data[sub]
            else:
                for file_type in file_data[sub].keys():
                    if file_type not in out_data[sub].keys():
                        out_data[sub][file_type] = file_data[sub][file_type]
                    else:
                        assert type(out_data[sub][file_type]) == list
                        for new_path in file_data[sub][file_type]:
                            if new_path not in out_data[sub][file_type]:
                                out_data[sub][file_type].append(new_path)
    
    out_dirs = '/'.join(out_path.split('/')[:-1])
    os.makedirs(out_dirs, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=4)
