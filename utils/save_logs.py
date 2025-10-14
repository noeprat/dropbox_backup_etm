import json
from .filename_reader import create_filename_dict, remove_extension
import os

def save_file_infos(input_files, participants_dict, out_path, **kwargs):
    final_data= {}
    for file in input_files:
        print(file)
        final_data[file] = create_filename_dict(file, participants_dict, **kwargs)
    print('done')

    with open(out_path, 'w') as f:
        json.dump(final_data, f, indent=4)


def save_jsons_to_data(file_infos_path, jsons_to_data_path):
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
            data_new_path = json_file_infos['new_path']
            json_new_path = remove_extension(data_new_path) + '.json'

            json_file_infos['new_path'] = json_new_path
            file_infos[json_file] = json_file_infos

    with open(corrected_file_infos_path, 'w') as f:
        json.dump(file_infos, f, indent=4)



def write_paths_file(file_infos_path, out_path, old_prefix='', new_prefix=''):

    with open(file_infos_path,'r') as f:
        data = json.load(f)
    
    out_dirs = '/'.join(out_path.split('/')[:-1])
    try:
        os.makedirs(out_dirs)
        with open(out_path,'w') as f:
            for file in data.keys():
                f.write('~' + old_prefix + data[file]['old_path'] + ', ~/' + new_prefix + data[file]['new_path'])
                f.write('\n')
    except:
        with open(out_path,'a') as f:
            for file in data.keys():
                f.write('~' + data[file]['old_path'] + ', ~/' + data[file]['new_path'])
                f.write('\n')


def write_general_recap_file(file_infos_path, out_path, new_prefix=''):
    with open(file_infos_path,'r') as f:
        file_infos = json.load(f)
    
    out_dirs = '/'.join(out_path.split('/')[:-1])
    out_data = {}

    try:
        with open(out_path,'w') as f:
            for file in file_infos.keys():
                type = file_infos[file]['type']
                new_path = new_prefix + file_infos[file]['new_path']
                sub = file_infos[file]['sub']
                if sub not in out_data.keys():
                    out_data[sub] = {}
                if type in out_data[sub].keys():
                    out_data[sub][type].append(new_path)
                else:
                    out_data[sub][type] = [new_path]
            json.dump(out_data, f, indent=4)
    except:
        try:
            os.makedirs(out_dirs)
        finally:
            with open(out_path,'w') as f:
                for file in file_infos.keys():
                    type = file_infos[file]['type']
                    new_path = new_prefix + file_infos[file]['new_path']
                    sub = file_infos[file]['sub']
                    if sub not in out_data.keys():
                        out_data[sub] = {}
                    if type in out_data[sub].keys():
                        out_data[sub][type].append(new_path)
                    else:
                        out_data[sub][type] = [new_path]
                json.dump(out_data, f, indent=4)
        

def merge_general_recaps(input_files, out_path):
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
    try:
        with open(out_path, 'w') as f:
            json.dump(out_data, f, indent=4)
    except:
        out_dirs = '/'.join(out_path.split('/')[:-1])
        os.makedirs(out_dirs)
        with open(out_path, 'w') as f:
            json.dump(out_data, f, indent=4)
