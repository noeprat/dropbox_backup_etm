from utils.dropbox_filesystem import get_all_paths, sort_source_to_target
from utils.save_logs import save_file_infos, save_jsons_to_data, correct_file_infos_with_matching_metadata 
from utils.save_logs import write_paths_file, write_general_recap_file, merge_general_recaps, refresh_new_paths
from utils.handle_duplicates import flag_potential_duplicates, rename_duplicates

from tokens import ACCESS_TOKEN

import csv

if __name__ == '__main__':
    s= "Should the Dropbox token be refreshed ? [y/n]"

    if s=='y':
        ACCESS_TOKEN = input('new access token:')


    input_files = get_all_paths(TOKEN= ACCESS_TOKEN, 
                            dir= '/source', 
                            recursive=True, 
                            remove_source=True
                            )
    print('Done reading files from Dropbox \n')

    subdir = input('subdir')
    n = input('n')

    file_infos_path = 'file_infos/'+ subdir +'/file_infos-' + n + '.json'

    jsons_to_data_path = 'file_infos/'+ subdir +'/jsons_to_data-' + n + '.json'

    corrected_file_infos_path = file_infos_path[:-len('.json')] +'_corrected.json'

    flagged_path = 'file_infos/'+ subdir +'/potential_duplicates-' + n + '.json'

    renamed_duplicates_file_infos_path = corrected_file_infos_path[:-len('.json')] +'_renamed_duplicates.json'


    txt_logs_path = 'paths/' + subdir + '/paths-' + n + '.txt'

    json_recap_path = 'recaps/' + subdir + '/recap-' + n + '.json'


    old_prefix = input('old_prefix')
    new_prefix = input('new_prefix')

    sub = input('sub (like "sub-01" or "")')
    
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
    
    input('Manually correct the json in `jsons_to_data_path` to match each json to its correct data file (type enter when done to continue)')

    correct_file_infos_with_matching_metadata(
                    file_infos_path = file_infos_path,
                    jsons_to_data_path = jsons_to_data_path,
                    corrected_file_infos_path = corrected_file_infos_path
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
    

    print('Check and correct the file infos in ' + renamed_duplicates_file_infos_path + ' before continuing')
    s = input('Do you want to refresh the new paths ? [y/n]')

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
    

    


    