#!/usr/bin/env python

# Finds various information from files

import subprocess
from ciao_contrib.runtool import dmkeypar, dmlist


# Finding the ccd_id from file header #

def ccd_id_finder(obsid_list, ccd_id):

    for obs in obsid_list:
        if 1000 <= int(obs) < 10000:  # Note that obsID's with #### have a (0) in front of the _repro
            ccd = dmkeypar("%s/repro/acisf0%s_repro_evt2.fits" % (obs, obs), keyword='CCD_ID', echo='True')  # Get value of keyword 'CCD_ID'
        elif 0 < int(obs) < 1000:
            ccd = dmkeypar("%s/repro/acisf00%s_repro_evt2.fits" % (obs, obs), keyword='CCD_ID', echo='True')
        else:
            ccd = dmkeypar("%s/repro/acisf%s_repro_evt2.fits" % (obs, obs), keyword='CCD_ID', echo='True')
        ID = int(ccd)  # Make the number an integer instead of a ciao.string
        ccd_id.append(ID)  # stick to list
    return ccd_id


# Finding the start and stop times from dmlist #

def time_finder(obsid_list, ccd_id, times):

    for obs in obsid_list:
        time_output = subprocess.check_output(['dmlist', "reprojected_data/%s_background.fits[GTI%s]" % (obs, ccd_id[obsid_list.index(obs)]), 'data'])  # Captures the time list output of dmlist
        start = time_output[234:254]  # Gets the start time from the first row
        stop = time_output[-21:-1]  # Gets the stop time from the last row and deletes the /newline
        times.extend([start, stop])
    return times


# Define energy boundaries #

def energy_inp(energy):

    nrgy1 = raw_input("Input minimum energy filter value (KeV): ")
    nrgy2 = raw_input("Input maximum energy filter value (KeV): ")
    energy.extend([nrgy1, nrgy2])
    return energy


# Get coordinates of contbin_mask.reg file #

def get_coords(coord_values):

    cat = subprocess.check_output(['cat', 'contbin/contbin_mask.reg'])  # Captures output of 'cat', which has the region file coordinates
    cat_list = cat.split()  # Splits the output into list
    coord_string = cat_list[len(cat_list)-1]  # Get the shape and coordinates of the region
    dummy = coord_string.split('(')  # Splits at the first parenthesis
    if dummy[0] == 'rotbox':
        coordinates = dummy[1].split(',')  # Gives list of ['xcenter', 'ycenter', 'width', 'height', 'angle']
        xcenter = float(coordinates[0])
        ycenter = float(coordinates[1])
        width = float(coordinates[2])
        height = float(coordinates[3])
        xstart = xcenter - (width/2)
        xend = xcenter + (width/2)
        ystart = ycenter - (height/2)
        yend = ycenter + (height/2)
        coord_values.extend([xstart, xend, ystart, yend])  # Stick to coord_values list
    if cat[0:3] == 'box':
        coord_string = cat_list[0].split(',')
        coord_string[0] = coord_string[0][4:]  # Delete the 'box(' in index 0
        xcenter = float(coord_string[0])
        ycenter = float(coord_string[1])
        width = float(coord_string[2])
        height = float(coord_string[3])
        xstart = xcenter - (width/2)
        xend = xcenter + (width/2)
        ystart = ycenter - (height/2)
        yend = ycenter + (height/2)
        coord_values.extend([xstart, xend, ystart, yend])  # Stick to coord_values list
    return coord_values
