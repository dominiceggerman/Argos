#!/usr/bin/env python

# Deflaring #

import os
from ciao_contrib.runtool import dmcopy, dmextract, deflare


# Deflare #

def extract_flare(obsid_list, times):

    count = 1
    for obs in obsid_list:  # Cycles through obsID's
        binlength = raw_input('Select bin length, (usually 200): ')  # Bin set to 200
        index1 = (count*2)-2  # Gets the start time index of the obsID
        index2 = (count*2)-1  # Gets the stop time index of the obsID
        start = times[index1]  # Selects the start and stop times for the obsID being run
        stop = times[index2]
        count += 1  # Adds 1 to the count to continue formula ie. obsID number 3 will have count = 3, index1=4, and index2=5 which are its start and stop times in the times list
        print "Performing dmextract and deflare on obsID %s" % obs
        dmextract(infile="reprojected_data/%s_background.fits[bin time=%s:%s:%s]" % (obs, start, stop, binlength), outfile='reprojected_data/%s_background.lc' % obs, opt='ltc1', clobber='yes')
        deflare(infile='reprojected_data/%s_background.lc' % obs, outfile='reprojected_data/%s_bkg_deflare.gti' % obs, method='clean', plot='no', save='reprojected_data/%s_plot' % obs)


# Checks with user to confirm the binning amount #

def flare_checker(obsid_list, times):
    choice = raw_input("Is the binning what you wanted? (yes/no): ")
    for decision in choice:
        if choice == "yes":
            break
        elif choice == "no":  # Loops infinitly if you keep hitting "no" until a desired bin is found.
            os.system('rm reprojected_data/*_bkg_deflare.gti')
            os.system('rm reprojected_data/*_background.lc')
            extract_flare(obsid_list, times)
            break
        else:
            choice = raw_input("Enter yes or no: ")


# If deflare was successful #

def evt_list_filt(obsid_list):

    for obs in obsid_list:
        dmcopy(infile='reprojected_data/%s_efilter.fits[@%s_bkg_deflare.gti]' % (obs, obs), outfile='reprojected_data/%s_reproj_clean.fits' % obs, clobber='yes')
