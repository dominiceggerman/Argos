# Argos Chandra Data Reduction and Mapping of Spectral Properties #

# By Dominic Eggerman #
# Special thanks to Grant Tremblay for his contributions #

# Module Imports #

import sys
import os
import subprocess
import glob
import numpy

# Script imports #

from Argos import make_dirs
from Argos import obsID_select
from Argos import basic_redux
from Argos import info_finder
from Argos import filter_data
from Argos import deflare
from Argos import blank_sky
from Argos import make_binmap
from Argos import extract_spectra
from Argos import fit_spectra
from Argos import paint_images

# CIAO Imports #

if os.environ.get("CALDB") is None:
    sys.exit('Please initalize CIAO before running this script.')
else:
    from ciao_contrib.runtool import dmcopy, dmmakepar, dmreadpar, dmextract
    from ciao_contrib.runtool import dmkeypar, dmlist, chandra_repro, flux_obs
    from ciao_contrib.runtool import reproject_events, deflare, specextract
    from ciao_contrib.runtool import acis_bkgrnd_lookup
    import sherpa.astro.ui as sherpa


def Argos(directory, obsid_list, energy, energy_eV, ccd_id, times, coord_values, redshift, nH_Gal, obs_auto_sel, multiprocessing, processes, deflare_opt, large_source, wght):

    """
    Inputs: directory - Directory for the work. Default is current. Change with options when launching script.
            obsid_list - A list of the obsids. Selected after launch.
            energy - The energy constraints. Default is 0.5 - 7.0 KeV. Change with options when launching script.
            energy_eV - Same as energy but in eV
            ccd_id - A list of the ccd_ids whose index match to the that of the obsid list. Automatically found when running script.
            times - A list of the times to filter the observations if deflare is required. Found automatically.
            coord_values - The coordinates of the contbin region where spectral maps will be created. Found automatically after contbin box is created.
            redshift - Redshift of the source. Taken from command line input.
            nH_Gal - Galactic nH (10^22 cm^-2). Taken from command line input.
            obs_auto_sel - Default = False. If True will automatically select obsids from working directory.
            multiprocessing - Default = True. Runs multiprocessing on spectral extraction.
            processes - Number of processes for multiprocessing.
            deflare_opt - Default = False. If True will run deflaring.
            large_source - Default = False. If True will create blank sky backgrounds for an extended source.
            wght - Default = 'no'. Weighting of arfs for extracting spectra.

    #####

    Final spectral maps are outputted to the final_maps folder.
    """

    # Change into desired directory
    os.chdir(directory)

    # Make directories for work #
    make_dirs.mkdir()
    print('Basic directories have been created or already exist')

    # User selection of obsID's #
    obsID_select.obsID_selection(obsid_list, obs_auto_sel)  # Feed in empty list, return numerically sorted list
    print('Obsids selected: ')
    print(obsid_list)

    # Check if obsID's have been downloaded, and download if not found #
    for obs in obsid_list:
        if os.path.exists(directory + '/' + obs + '/primary'):
            print('Found obsID directory for obs %s' % obs)
        else:
            os.system('download_chandra_obsid %s' % obs)

    # Reprocess events with chandra_repro #
    basic_redux.lvl2_data(obsid_list)
    # Align observations to the same WCS space #
    basic_redux.WCS(obsid_list)
    # Use DS9 to make background and cluster regions #
    basic_redux.deep_space_9()
    # Check that regions have been made #
    basic_redux.reg_file_check()

    # Get ccd_id info #
    info_finder.ccd_id_finder(obsid_list, ccd_id)  # Feed empty ccd_id list, return list of ccd_ids whose index correspond to the obsid index in obsid_list

    if deflare_opt is True:
        # Filter data by energy #
        filter_data.espace_filt(obsid_list, ccd_id, energy_eV)  # Energy needs to be inputted in eV
        filter_data.bkg_lightcurve(obsid_list)
        # Find times for deflaring #
        info_finder.time_finder(obsid_list, ccd_id, times)  # Feed empty energy list, return start and stop times
        # Deflare #
        deflare.extract_flare(obsid_list, times)
        deflare.flare_checker(obsid_list, times)
        deflare.evt_list_filt(obsid_list)

    # Detect evt2_file to use for blank sky backgrounds and spectra extraction (further down) #
    if deflare_opt is True:
        evt2_file = '_reproj_clean.fits'
    else:
        evt2_file = '_reproj_evt.fits'

    # Use blank sky backgrounds if source is extended or covers the entire chip #
    if large_source is True:
        # Copy to the blank sky folder #
        blank_sky.bsky_organiser(evt2_file)
        # Get the background files #
        blank_sky.get_bkg(obsid_list, evt2_file)
        # Add pointing header keywords to the background file #
        blank_sky.evt2_pointer(obsid_list, evt2_file)
        # Reproject events with aspect solution files #
        blank_sky.aspect_sol(obsid_list, evt2_file)

    # Create contbin_mask.reg and get coordinate values #
    if os.path.exists(directory + '/contbin/contbin_mask.reg') is False:
        make_binmap.contbin_dir()
        make_binmap.contbin_reg_file_check()
    info_finder.get_coords(coord_values)  # Feed empty coord_value list, return physical coordinates of box region (xstart, xend, ystart, yend)

    # Creating region for contbin work and region files #
    make_binmap.reg_creator(coord_values, energy_eV)
    make_binmap.make_binmap_regions(directory, coord_values)

    # Extract and fit spectra #
    os.chdir(directory + '/spectral_maps/')
    regions = glob.glob('xaf_*.reg')  # Get regions
    regions.sort()
    if multiprocessing:
        extract_spectra.multi(obsid_list, regions, evt2_file, wght, processes)
    else:
        extract_spectra.extract_spec(obsid_list, regions, evt2_file, wght)
    fit_spectra.fit_sherpa(obsid_list, redshift, nH_Gal, energy)
    paint_images.paint_spectra_to_map(regions)
    os.chdir(directory)

    # Copy to final folder #
    os.system('cp spectral_maps/*.fits final_maps/')
    print('All data maps have been copied and can be viewed in the final_maps/ folder.')


if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] <redshift> <nH_Gal> \n\nArguments:\n  <redshift>    redshift of the source\n  <nH_Gal>      Galactic N_H (10^22 cm^-2)', version="%prog 0.6")
    parser.add_option('--directory', dest='directory', help='Directory for the work. Default is the current directory', metavar='STR', default='./')
    parser.add_option('--define_e', action='store_true', dest='define_e', help='Specify energy filter. Default = 500 - 7000 eV', default=False)
    parser.add_option('--obs_auto', action='store_true', dest='obs_auto', help='Select obsids automatically from the current folder?', default=False)
    parser.add_option('--deflare', action='store_true', dest='deflare', help='Deflare the observation', default=False)
    parser.add_option('--bsky', action='store_true', dest='bsky', help='Make blank sky background (if source occupies most of the chip)', default=False)
    parser.add_option('--weight', action='store_true', dest='wght', help='Generate weighted arfs during specextract (source with large angular size)', default=False)
    parser.add_option('--multi', action='store_true', dest='multi', help='Disable multiprocessing for extracting spectra (not recommended. Default = True)', default=True)
    (options, args) = parser.parse_args()
    if len(args) == 2:
        # Parameter Lists #
        obsid_list = []
        energy = []
        energy_eV = []
        ccd_id = []
        times = []
        coord_values = []

        # Get directory #
        dir_temp = options.directory
        os.chdir(dir_temp)
        directory = os.getcwd()

        # Get parameters from input #
        redshift = args[0]
        nH_Gal = args[1]

        # Get options #
        obs_auto_sel = options.obs_auto
        define_energy = options.define_e
        deflare_opt = options.deflare
        large_source = options.bsky
        weight_arf = options.wght
        multiprocessing = options.multi

        # Get energy #
        if define_energy is False:
            energy.extend([0.5, 7.0])  # If no energy is specified
        else:
            info_finder.energy_inp(energy)  # If energy needs to be specified
        for e in energy:  # get energy in eV
            energy_eV.append(int(float(e)*1000))

        # Get processes #
        if multiprocessing:
            processes = raw_input('Enter number of processes for multiprocessing: ')
        else:
            pass

        # Get weight #
        if weight_arf is True:
            wght = 'yes'
        else:
            wght = 'no'

        # Run Argos #
        Argos(directory, obsid_list, energy, energy_eV, ccd_id, times, coord_values, redshift, nH_Gal, obs_auto_sel, multiprocessing, processes, deflare_opt, large_source, wght)

    else:
        parser.print_help()
