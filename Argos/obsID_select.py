#!/usr/bin/env python

# ObsID selection #

import glob


# Selecting obsID's #

def obsID_selection(obsid_list, obs_auto_sel):

    # Automatically select obsids #
    if obs_auto_sel is True:
        dirs = glob.glob('*')
        obsids = [n for n in dirs if n.isdigit()]
        for obs in obsids:
            obsid_list.append(obs)
        return obsid_list

    # Manually select obsids #
    else:
        count = 1
        while 1:
            obsid = raw_input("Enter obsID %d (Press enter on blank entry to terminate addition): " % count)  # Inputting obsID's and counting up
            obsid_list.append(obsid)  # Adding obsID's to the list
            count += 1
            if obsid == '':  # Enter breaks the loop
                del obsid_list[-1]  # Removing the last addition to the list which is the enter --> ['####','####','']
                obsid_list.sort(key=int)  # Sort the list
                return obsid_list
                break
