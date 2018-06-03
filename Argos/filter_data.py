#!/usr/bin/env python

from ciao_contrib.runtool import dmcopy

# Filter the reprojected files in energy space #

def espace_filt(obsid_list, ccd_id, energy):

    for obs in obsid_list:
        dmcopy(infile='reprojected_data/%s_reproj_evt.fits[energy=%s:%s, ccd_id=%s]' % (obs, energy[0], energy[1], ccd_id[obsid_list.index(obs)]), outfile='reprojected_data/%s_efilter.fits' % obs, opt='all', clobber='yes')


# Create background lightcurve #

def bkg_lightcurve(obsid_list):

    for obs in obsid_list:
        dmcopy(infile='reprojected_data/%s_efilter.fits[exclude sky=region(cluster.reg)]' % obs, outfile='%s_background.fits' % obs, opt='all', clobber='yes')
