from utils.dropbox_filesystem import get_all_paths, sort_source_to_target
from utils.save_logs import save_file_infos, save_file_list, read_file_list, save_jsons_to_data, correct_file_infos_with_matching_metadata 
from utils.save_logs import write_paths_file, write_general_recap_file, refresh_new_paths
from utils.handle_duplicates import flag_potential_duplicates, rename_duplicates, compare_potential_duplicates, handle_duplicates_in_file_infos

from tokens import ACCESS_TOKEN

import csv
import json

def input_with_default(input_name):
    try:
        with open('inputs.json', 'r') as f:
            default_inputs = json.load(f)
    except:
        default_inputs = {}
    new_inputs = default_inputs.copy()

    if input_name in default_inputs.keys():
        if len(default_inputs[input_name]) < 100:
            res = input(input_name + ': (default: ' + default_inputs[input_name] +') \n')
        else:
            res = input(input_name + ': (default: ' + default_inputs[input_name][:100] +'...) \n')
        if res == '':
            to_return = default_inputs[input_name]
        else:
            to_return = res
            new_inputs[input_name] = res
    else:
        to_return = input(input_name + ': \n')
        new_inputs[input_name] = to_return
    try:
        with open('inputs.json', 'w')as f:
            json.dump(new_inputs, f, indent=4)
    except:
        print('could not update inputs.json')
    return to_return



if __name__ == '__main__':

    subdir = input_with_default('subdir')
    n = input_with_default('n')

    file_list_path = 'file_list/' + subdir + '/file_list-' + n + '.json'

    file_infos_path = 'file_infos/'+ subdir +'/file_infos-' + n + '.json'

    jsons_to_data_path = 'file_infos/'+ subdir +'/jsons_to_data-' + n + '.json'

    corrected_file_infos_path = file_infos_path[:-len('.json')] +'_corrected.json'

    flagged_path = 'file_infos/'+ subdir +'/potential_duplicates-' + n + '.json'

    actual_duplicates_path = 'file_infos/'+ subdir +'/actual_duplicates-' + n + '.json'

    renamed_duplicates_file_infos_path = corrected_file_infos_path[:-len('.json')] +'_renamed_duplicates.json'


    txt_logs_path = 'paths/' + subdir + '/paths-' + n + '.txt'

    json_recap_path = 'recaps/' + subdir + '/recap-' + n + '.json'


    old_prefix = input_with_default('old_prefix')
    new_prefix = input_with_default('new_prefix')

    sub = input_with_default('sub')

    print('Need an access token for Dropbox')
    ACCESS_TOKEN = input_with_default('access token')

    s0= input("Should the files in Dropbox be read ? (can be a time-consuming step, and requires a dbx access token)\n[y/n]")

    if s0 == 'y':

        
        

        input_files = get_all_paths(TOKEN= ACCESS_TOKEN, 
                                dir= '/source', 
                                recursive=True, 
                                remove_source=True
                                )
        print('Done reading files from Dropbox \n')

        save_file_list(input_files, file_list_path)
    
    else:
        print('Reading file list from ' + file_list_path)

        input_files = read_file_list(file_list_path)
    
    if sub=='':
        participants_dict = {}

        try:
            with open('participants.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    left = row[0].strip()
                    right = row[1].strip()
                    if left != 'old_sub_name':
                        participants_dict[left] = right
        except:
            print('participants.csv not found')

        finally:    
            save_file_infos(
                input_files,
                participants_dict=participants_dict,
                out_path= file_infos_path
                )
    else:
        save_file_infos(
                input_files,
                participants_dict={},
                out_path= file_infos_path,
                sub=sub)
    
    # handle duplicates

    save_jsons_to_data(
        file_infos_path = file_infos_path,
        jsons_to_data_path= jsons_to_data_path)
    
    input('Manually correct the json in ' +jsons_to_data_path+ ' to match each json to its correct data file (type enter when done to continue)')

    correct_file_infos_with_matching_metadata(
                    file_infos_path = file_infos_path,
                    jsons_to_data_path = jsons_to_data_path,
                    corrected_file_infos_path = corrected_file_infos_path
                )    

    flag_potential_duplicates(
                    file_infos_path=corrected_file_infos_path,
                    flagged_path= flagged_path
                )
    print('Flagged duplicates in '+ flagged_path)
    s = input('Compare the potential duplicates (possibly a time-consuming step, requires a dropbox access token)? [y/n] \n')
    
    if s == 'y':
        compare_potential_duplicates(
            flagged_path=flagged_path,
            actual_duplicates_path=actual_duplicates_path,
            TOKEN= ACCESS_TOKEN,
            verbose= True
        )

        handle_duplicates_in_file_infos(
            actual_duplicates_path=actual_duplicates_path,
            file_infos_path= corrected_file_infos_path,
            new_file_infos_path= corrected_file_infos_path
        )

        flag_potential_duplicates(
                        file_infos_path=corrected_file_infos_path,
                        flagged_path= flagged_path
                    )
    
    rename_duplicates(
                    corrected_file_infos_path,
                    flagged_path,
                    renamed_duplicates_file_infos_path
                )
    

    print('\nCheck and correct the file infos in ' + renamed_duplicates_file_infos_path + ' before continuing \n')
    s = input('Do you want to refresh the new paths ? [y/n] \n')

    if s == 'y':
        refresh_new_paths(
                    renamed_duplicates_file_infos_path,
                    renamed_duplicates_file_infos_path
                )
    
        flag_potential_duplicates(
                        file_infos_path=renamed_duplicates_file_infos_path,
                        flagged_path= flagged_path
                    )
        
        rename_duplicates(
                        renamed_duplicates_file_infos_path,
                        flagged_path,
                        renamed_duplicates_file_infos_path
                    )

    print('\nLast chance to correct ' + renamed_duplicates_file_infos_path + ' before saving logs and copying files in Dropbox \n')
    input('Type enter to continue')

    # Save paths.txt and recap.json



    write_paths_file(
        file_infos_path= renamed_duplicates_file_infos_path,
        out_path = txt_logs_path,
        old_prefix=old_prefix,
        new_prefix=new_prefix
        )
    
    print('Path log saved in ' + txt_logs_path)
    
    write_general_recap_file(
        file_infos_path= renamed_duplicates_file_infos_path,
        out_path= json_recap_path,
        new_prefix=new_prefix
        )
    
    print('Recap saved in ' + json_recap_path)

    sort_source_to_target(
        file_infos_path= renamed_duplicates_file_infos_path,
        TOKEN=ACCESS_TOKEN
        )
    
    print('Files successfully copied in target directory')