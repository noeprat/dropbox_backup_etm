def pick_largest_str_in_list(str_list):
    res = ''
    for s in str_list:
        if len(s) > len(res):
            res = s
    return res