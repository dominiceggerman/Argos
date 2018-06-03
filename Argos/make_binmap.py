#!/usr/bin/env python

# Contour Binning #

import os
import subprocess
from ciao_contrib.runtool import dmcopy


# Creating directory for work #

def contbin_dir():

    os.system('cp reprojected_data/merged_evt.fits contbin/')  # Copies merged-evt.fits over from reprojected_data to contbin folder
    print('\nMake a box region around the target to obtain the x and y coordinates to input (physical coordinates in ds9)...')
    print('Make sure to save the region as contbin_mask.reg (ciao format) in the contbin folder in the projects parent directory')
    os.system('ds9 contbin/merged_evt.fits')  # Opens merged_evt.fits in ds9


# Check reprojected_data/ for the .reg file #

def contbin_reg_file_check():

    raw_input("Press Enter to continue when the files have been saved...")
    if os.path.exists("contbin/contbin_mask.reg") is True:
        print('The file contbin_mask.reg has been found')
    else:
        print('Please create contbin_mask.reg in DS9 (save as ciao file) and save it to contbin/')
        contbin_dir()


# Creating the region for contbinning work #

def reg_creator(coord_values, energy):

    # energy[0],[1] are [low],[high]
    # coord_values[0],[1],[2],[3] are [xstart],[xend],[ystart],[yend]
    os.system("dmcopy 'contbin/merged_evt.fits[energy=%s:%s][bin x=%s:%s:1, y=%s:%s:1]' contbin/contbin_input.fits clobber=yes" % (energy[0], energy[1], coord_values[0], coord_values[1], coord_values[2], coord_values[3]))


# Farith step and preparation to make region files #

def make_binmap_regions(directory, coord_values):

    ###### Need heasoft - maybe something to check that it is installed and need a way to call the program, also need it for contbin ?? ######
    os.chdir(directory + '/contbin/')  # Need to change into contbin directory so that contbin can output to the directory
    os.system("farith contbin_input.fits 0 temp.fits MUL")
    os.system("farith temp.fits 1 allones.fits ADD")
    os.system("rm temp.fits")
    dmcopy(infile='allones.fits[sky=region(contbin_mask.reg)][opt full]', outfile='mask.fits')
    os.system("rm allones.fits")
    sn = raw_input("Input signal to noise (sn) (e.g. 30): ")
    constrain_val = raw_input("Input constrainval value (e.g. 2.0): ")
    os.system("contbin --mask=mask.fits --sn=%s --smoothsn=3 --constrainfill --constrainval=%s contbin_input.fits" % (sn, constrain_val))  # Create contbin binmap
    os.chdir(directory)
    os.system("make_region_files --minx=%s --miny=%s --bin=1 --outdir=spectral_maps/ contbin/contbin_binmap.fits" % (coord_values[0], coord_values[2]))
    os.system("cp contbin/contbin_binmap.fits spectral_maps/")  # Copy contbin_binmap
