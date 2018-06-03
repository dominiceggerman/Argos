#!/usr/bin/env python

# Extract Spectra #

import glob
import os
from ciao_contrib.runtool import specextract
from multiprocessing import Pool


# Extracting spectra for regions of the target #
# Directory has been changed to spectral_maps/ #

# With multiprocessing #

def multi(obsid_list, regions, evt2_file, wght, processes):

    p = Pool(int(processes))
    reg_no = [r[:-4] for r in regions]
    for obs in obsid_list:
        print('ObsID: %s extracting...' % obs)
        info_list = [r + '_' + str(obs) + evt2_file + '_' + wght for r in reg_no]
        p.map(extract_multi, info_list)
        info_list = []


def extract_multi(info):

    info = info.split('_')

    obs = info[2]
    reg = info[0] + '_' + info[1] + '.reg'
    root = info[0] + '_' + info[1] + '_' + info[2]
    evt2_file = '_' + info[3] + '_' + info[4]
    wght = info[5]

    reg_total = len(glob.glob('xaf_*.reg'))
    reg_done = len(glob.glob('xaf_*_%s.pi') % str(obs))
    print('Completed %s/%s regions' % (reg_done, reg_total))
    if os.path.isfile(root + '.pi') is False:
        evt2_filter = '../reprojected_data/' + obs + evt2_file + '[sky=region(%s)]' % reg  # evt file for obsid with xaf.reg filter
        bkg_reg = '../reprojected_data/background.reg'
        bkg_filter = '../reprojected_data/' + obs + evt2_file + '[sky=region(%s)]' % bkg_reg  # using the reproj_evt file with the background region
        asp_file = '../reprojected_data/' + obs + '.asol'
        bpix_file = '../reprojected_data/' + obs + '.bpix'
        msk_file = '../reprojected_data/' + obs + '.mask'
        os.system('punlearn specextract')
        # Extract spectra
        specextract(infile=evt2_filter, outroot=root, bkgfile=bkg_filter, asp=asp_file, badpixfile=bpix_file, mskfile=msk_file, weight=wght)
    else:
        print('File %s.pi found' % root)


# Without Multiprocessing #

def extract_spec(obsid_list, regions, evt2_file, wght):

    for reg in regions:
        for obs in obsid_list:
            root = reg[:-4] + '_' + obs
            # Check if spectra has been extracted for the region and obsid #
            if os.path.isfile(root + '.pi') is False:
                print('Extracting spectra for obsid %s/%s: Completed %s/%s regions...' % (obsid_list.index(obs)+1, len(obsid_list), regions.index(reg)+1, len(regions)))
                evt2 = glob.glob('../reprojected_data/' + str(obs) + evt2_file)  # evt file for obsid
                evt2_filter = evt2[0] + '[sky=region(%s)]' % reg  # add xaf.reg filter
                bkg_reg = glob.glob('../reprojected_data/background.reg')
                bkg_filter = evt2[0] + '[sky=region(%s)]' % bkg_reg[0]  # using the reproj_evt file with the background region
                asp_file = glob.glob('../reprojected_data/' + str(obs) + '.asol')
                asp_file = asp_file[0]  # Turn into string from glob list
                bpix_file = glob.glob('../reprojected_data/' + str(obs) + '.bpix')
                bpix_file = bpix_file[0]
                msk_file = glob.glob('../reprojected_data/' + str(obs) + '.mask')
                msk_file = msk_file[0]
                os.system('punlearn specextract')  # Reset specextract
                # Extract spectra
                specextract(infile=evt2_filter, outroot=root, bkgfile=bkg_filter, asp=asp_file, badpixfile=bpix_file, mskfile=msk_file, weight=wght)
            else:
                print('Already extracted spectra for %s/%s obsids in %s/%s regions' % (obsid_list.index(obs)+1, len(obsid_list), regions.index(reg)+1, len(regions)))
