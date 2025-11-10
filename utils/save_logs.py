import json
from .filename_reader import create_filename_dict, generate_new_path, is_derivative
from .misc import remove_extension
import os

def save_file_list(input_files, file_list_path):
    """
    Saves a json in `file_list_path` containing all files in the source directory in the dropbox

    Parameters
    --------
        input_files : list(str),
            a list of path strings
        file_list_path : str,
            the path where the file list will be saved (usually of the type `/file_list/subdir/file_list-[n].json`)
    
    Saves
    --------
        file_list_path, json file
            the file list can be found as follows: input_files = file_list_path_dict['input_files']
    """

    data = {
        "input_files": input_files
    }

    try:
        dirs = '/'.join(file_list_path.split('/')[:-1])
        os.makedirs(dirs, exist_ok=True)
        with open(file_list_path, 'w') as f:
            json.dump(data, f, indent=4)
    except:
        with open(file_list_path, 'w') as f:
            json.dump(data, f, indent=4)


def read_file_list(file_list_path):
    with open(file_list_path, 'r') as f:
        data = json.load(f)
    input_files = data['input_files']
    return input_files



def save_file_infos(input_files, participants_dict, file_infos_path, tmpfile_infos_path, **kwargs):
    """
    Saves a json in `file_infos_path` containing information and sorting instructions ("new_path") for all files in `input_files`

    Kwargs can be used to pre-determine some information

    Parameters
    --------
        input_files : list(str),
            a list of path strings
        participants_dict : dict,
            new sub name given to the former one (e.g. participants_dict['REEVOID_PILOT_01'] = 'sub-pilot')
        file_infos_path : str,
            the path where the file infos will be saved (usually of the type `/file_infos/subdir/file_infos-[n].json`)
        tmpfile_infos_path : str,
            the path where the file infos (for temporary files) will be saved (usually of the type `/file_infos/subdir/tmp_file_infos-[n].json`)
        **kwargs
    
    Saves
    --------
        file_infos_path, json file
            information about a file can be found as follows: file_infos_path[file]['new_path'] or out_path_dict[file]['type'] etc.

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
    tmp_files_infos = {}
    for file in input_files:
        #print(file)
        file_infos = create_filename_dict(file, participants_dict, **kwargs)
        is_tmp_bool = file_infos['is_tmp']

        if (not is_tmp_bool):
            final_data[file] = file_infos
        else:
            tmp_files_infos[file] = file_infos


    print('done')

    try:
        dirs = '/'.join(file_infos_path.split('/')[:-1])
        os.makedirs(dirs, exist_ok=True)
        with open(file_infos_path, 'w') as f:
            json.dump(final_data, f, indent=4)
        with open(tmpfile_infos_path, 'w') as f:
            json.dump(tmp_files_infos, f, indent=4)
    except:
        with open(file_infos_path, 'w') as f:
            json.dump(final_data, f, indent=4)
        with open(tmpfile_infos_path, 'w') as f:
            json.dump(tmp_files_infos, f, indent=4)

def refresh_new_paths(file_infos_path, new_file_infos_path):
    """
    Saves a json in `new_file_infos_path` which is a copy of `file_infos_path` with consistent new filenames

    **Overwrites the file in `out_path`**

    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        new_file_infos_path : str,
            path to updated fileinfos (can be the same as the original fileinfos, which will update it)
    
    Saves
    --------
        new_file_infos_path, json file
            updated fileinfos
    """
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
    new_file_infos = file_infos.copy()
    for file in file_infos.keys():
        #print(file_infos[file].keys()) # to debug
        try:
            seg_info = file_infos[file]['seg_info']
        except KeyError:
            seg_info = ''
        try:
            func_info = file_infos[file]['func_info']
        except KeyError:
            func_info = ''
        try:
            func_task = file_infos[file]['func_task']
        except KeyError:
            func_task = ''
        
        should_be_refreshed = True
        if 'confirmed_duplicate' in file_infos[file].keys():
            if file_infos[file]['confirmed_duplicate']:
                should_be_refreshed = False
        
        if should_be_refreshed:
            new_path = generate_new_path(
                old_path= file_infos[file]['old_path'],
                sub = file_infos[file]['sub'],
                id = file_infos[file]['id'],
                type = file_infos[file]['type'],
                category = file_infos[file]['category'],
                seg_info = seg_info,
                func_task= func_task,
                func_info= func_info,
                suffix = file_infos[file]['suffix'],
                extension = file_infos[file]['extension'],
                is_tmp_bool = file_infos[file]['is_tmp'],
                is_derivative_bool = file_infos[file]['is_derivative'],
                is_localizer_bool = file_infos[file]['is_localizer'],
                is_other_bool = file_infos[file]['is_other'],
                is_a_previous_version_bool = file_infos[file]['is_a_previous_version']
            )
            new_file_infos[file]['new_path'] = new_path
    
    with open(new_file_infos_path, 'w') as f:
        json.dump(new_file_infos, f, indent=4)


def save_jsons_to_data(file_infos_path, jsons_to_data_path, debug=False):
    """
    Saves a json in `jsons_to_data_path` matching metadata files with their respective data


    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        jsons_to_data_path : str,
            the path where the matches will be saved (usually of the type `/file_infos/subdir/jsons_to_data-[n].json`)
        debug : bool, default=False,
    
    Saves
    --------
        jsons_to_data_path, json file
            metadata-data connections can be found as follows: jsons_to_data_path_dict[json_file] = list(possible matching data files)

    """
    jsons_dict = {}

    data_dict = {}

    out_dict = {}

    strs_to_remove = [
        '.',
        'dicoms_',
        't2g002_',
        'brain_',
        'nonanonymous_',
        'ct_'
    ]

    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
        all_files = file_infos.keys()

        for file in all_files:
            try:
                file_is_a_duplicate = file_infos[file]["confirmed_duplicate"]
            except:
                file_is_a_duplicate=False
            if not file_is_a_duplicate:
                if file_infos[file]['extension'] == '.json' and file[-len('_ctd.json'):]!='_ctd.json':
                    jsons_dict[file] = file_infos[file]
                else:
                    data_dict[file] = file_infos[file]
    if debug:
        c=0

    for json_file in jsons_dict.keys():
        json_filename = json_file.split('/')[-1][:-len('.json')].lower()
        out_dict[json_file] = []
        for data_file in data_dict.keys():
            filename = data_file.split('/')[-1].lower()
            curated_filename = remove_extension(filename)
            curated_json_filename = json_filename
            for s in strs_to_remove:
                curated_json_filename = curated_json_filename.replace(s,'')
                curated_filename = curated_filename.replace(s,'')
            if debug and c<10:
                print('file: \n    ', filename)
                print('curated json filename: \n    ', curated_json_filename)
                c += 1
            condition3 = False
            if filename == 'fmri.nii.gz':
                tasks_json = [
                    side + part
                    for side in ['l','r']
                    for part in ['ankle','knee', 'hip', 'grasp']
                ]
                tasks_json.append('restingstate')
                tasks_nifti = [
                    side +'_'+ part
                    for side in ['left','right']
                    for part in ['ankle','knee', 'hip', 'grasp']
                ]
                tasks_nifti.append('rest')
                for idx, task in enumerate(tasks_json):
                    if task in json_file.lower() and tasks_nifti[idx] in data_file.lower():
                        condition3 = True
            condition1 = curated_json_filename == curated_filename
            condition2 = json_filename == filename

            if condition1 or condition2 or condition3:
                out_dict[json_file].append(data_file)

    with open(jsons_to_data_path, 'w') as f:
        json.dump(out_dict, f, indent=4)


def correct_file_infos_with_matching_metadata(file_infos_path, jsons_to_data_path, corrected_file_infos_path, verbose=False, debug=False):
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
        verbose : bool, default = False,
            will print some steps if set to True
        debug : bool, default = False,
            will print some variables for debugging if set to True
    
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
        if len(jsons_to_data[json_file])==0:
            print('found no matching data file for: ', json_file)
        if len(jsons_to_data[json_file])>1 and verbose:
            print('found several matching data files for: ', json_file)
            print('By default, this file will be considered as the matching data file: \n   ', jsons_to_data[json_file][0])
        if len(jsons_to_data[json_file])>=1:
            matching_file = jsons_to_data[json_file][0]
            matching_file_infos = file_infos[matching_file].copy()
            json_file_infos = file_infos[matching_file].copy()
            json_file_infos['extension'] = '.json'
            json_file_infos['old_path'] = file_infos[json_file]['old_path']

            if debug:
                print('json_file', json_file)
                print('matching_file', matching_file)
            
            for key in ['id', 'suffix', 'seg_info', 'func_info', 'func_task']:
                try:
                    old_json_value = file_infos[json_file][key]
                except:
                    old_json_value = ''
                try:
                    matching_file_value = file_infos[matching_file][key]
                except:
                    matching_file_value = ''
                
                if debug:
                    print('key',key)
                    print('matching_file_value', matching_file_value)
                    print('old_json_value', old_json_value)

                if matching_file_value == '' and old_json_value !='':
                    json_file_infos[key] = old_json_value
                    matching_file_infos[key] = old_json_value
            for key in matching_file_infos.keys():
                if key not in ['old_path', 'extension', 'new_path']:
                    json_file_infos[key] = matching_file_infos[key]

            file_infos[json_file] = json_file_infos
            file_infos[matching_file] = matching_file_infos

    with open(corrected_file_infos_path, 'w') as f:
        json.dump(file_infos, f, indent=4)
    
    refresh_new_paths(corrected_file_infos_path, corrected_file_infos_path)



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
    
    
    
    os.makedirs(out_dirs, exist_ok=True)
    with open(out_path,'w') as f:
        for file in data.keys():
            try:
                is_duplicate_bool = data[file]['confirmed_duplicate']
            except:
                is_duplicate_bool= 'confirmed_duplicates' in data[file]['new_path']
            is_tmp_bool = data[file]['is_tmp']
            
            if is_tmp_bool:
                f.write('# ~' + corrected_old_prefix + data[file]['old_path'] + ' was not copied (TMP)')
                f.write('\n')
            
            elif is_duplicate_bool:
                f.write('# ~' + corrected_old_prefix + data[file]['old_path'] + ' was not copied (duplicate)')
                f.write('\n')

            else:
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
            try:
                is_duplicate_bool = file_infos[file]['confirmed_duplicate']
            except:
                is_duplicate_bool= 'confirmed_duplicates' in new_path

            sub = file_infos[file]['sub']
            if (not is_tmp_bool) and (type != 'misc') and (not is_duplicate_bool):
                if sub not in out_data.keys():
                    out_data[sub] = {}
                if type not in out_data[sub].keys():
                    out_data[sub][type] = []
                out_data[sub][type].append(new_path)
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
