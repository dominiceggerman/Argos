#!/usr/bin/env python

# Blank Sky Backgrounds #

import os
import glob
from ciao_contrib.runtool import dmcopy, dmmakepar, dmreadpar
from ciao_contrib.runtool import reproject_events, acis_bkgrnd_lookup


# Organise blank sky work #

def bsky_organiser(evt2_file):

    os.system('cp reprojected_data/*' + evt2_file + ' blank_sky/')  # Copy all of the ####_reproj_clean.fits or ####_reproj_evt.fits files to the blank sky folder


# Get the background file #

def get_bkg(obsid_list, evt2_file):

    for obs in obsid_list:
        obs_file = str(obs)+evt2_file
        acis = acis_bkgrnd_lookup(infile='reprojected_data/%s' % obsfile)
        os.system("cp %s blank_sky/%s_bkgevt2.fits" % (acis, obs))  # Copies the acis file and renames it
        dmcopy(infile='blank_sky/%s_bkgevt2.fits[status=0]' % obs, outfile='blank_sky/%s_bkgevt2_clean.fits' % obs)


# Add pointing header keywords to the background file #

def evt2_pointer(obsid_list, evt2_file):

    for obs in obsid_list:
        obs_file = str(obs)+evt2_file
        dmmakepar(infile='blank_sky/%s' % obs_file, outfile='blank_sky/%s_event_header.par' % obs)
        os.system("grep _pnt blank_sky/%s_event_header.par > blank_sky/%s_event_pnt.par" % (obs, obs))
    os.system("chmod +w blank_sky/*_bkgevt2_clean.fits")  # Make the clones writable
    for obs in obsid_list:
        dmreadpar(infile='blank_sky/%s_event_pnt.par' % obs, outfile='blank_sky/%s_bkgevt2_clean.fits[events]' % obs, clobber='True')  # Migrate the pointing header keywords to the new clones


# Find and copy aspect solution files over for reproject_events #

def aspect_sol(obsid_list, evt2_file):

    for obs in obsid_list:
        asp_file = [os.path.basename(x) for x in glob.glob('%s/repro/*pcad*asol*' % obs)]  # Captures only the basename of the file in the path and adds it in a list
        aspect = asp_file[0]  # Assigns the file to a variable
        os.system("cp %s/repro/*asol*.fits blank_sky" % obs)
        obs_file = str(obs)+evt2_file
        reproject_events(infile='blank_sky/%s_bkgevt2_clean.fits' % obs, outfile='blank_sky/%s_bkg_reproj_clean.fits' % obs, aspect='blank_sky/%s' % aspect, match='blank_sky/%s' % obs_file, random=0, verbose=5, clobber='True')
        del asp_file
        del aspect
