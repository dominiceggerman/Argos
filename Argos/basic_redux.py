#!/usr/bin/env python

# Basic Chandra data reduction #

import os
import glob
from ciao_contrib.runtool import chandra_repro, reproject_obs, flux_obs
from multiprocessing import Pool


# Reprocess events #

def lvl2_data(obsid_list):

    p = Pool(4)
    if len(glob.glob(obs+'/*/*evt2.fits')) == 1:
        print('Found obsID repro directory')
    else:
        p.map(repro_worker, obsid_list)

def repro_worker(obs):

    print('Reprocessing (chandra_repro) obsid %s' % obs)
    chandra_repro(indir='%s' % obs, outdir='%s/repro' % obs, verbose=0, cleanup='no')


# Align observations to the same WCS space #

def WCS(obsid_list):

    p = Pool(4)
    if os.path.exists('reprojected_data/%s_reproj_evt.fits' % obsid_list[0]) is False:
        p.map(reproject_worker, obsid_list)
    if os.path.exists('exposure_corrected_mosaic/broad_flux.img') is False:
        print('Combining reprojected observations to create exposure corrected image...')
        flux_obs(infiles='reprojected_data/*reproj_evt.fits', outroot='exposure_corrected_mosaic/', bands='broad,csc', bin=1, verbose=0)
        os.system('cp exposure_corrected_mosaic/broad_flux.img exposure_corrected_mosaic/broad_flux.fits')
    print('\nCreate circular regions around the target and a background portion of the image.')
    print('Save the target region as cluster.reg and the background region as background.reg.')
    print('Save both in /reprojected_data/.  Make sure to save the regions in ciao format in physical coordinates.')

def reproject_worker(obs):

    print('Reprojecting observations for obs %s...' % obs)
    reproject_obs(infiles='%s/repro/*evt2.fits' % obs, outroot='reprojected_data/', verbose=0)


# Opens DS9 #

def deep_space_9():

    raw_input("Press enter to open DS9, then close DS9 once you have fininshed making the files...")
    os.system('ds9 exposure_corrected_mosaic/broad_flux.fits')


# Checks reprojected_data/ for the .reg files #

def reg_file_check():

    raw_input("Press Enter to continue when the files have been saved...")
    if os.path.exists("reprojected_data/cluster.reg") is True:
        print "The file cluster.reg has been found"
    else:
        print "Please create cluster.reg in DS9 (save as ciao file) and save it to reprojected_data/"
        deep_space_9()
    if os.path.exists("reprojected_data/background.reg") is True:
        print "The file background.reg has been found"
    else:
        print "Please create background.reg in DS9 (save as ciao file) and save it to reprojected_data/"
        deep_space_9()
