#!/usr/bin/env python

# Fitting Spectra #

import sherpa.astro.ui as sherpa
import glob
import numpy


# Fit spectra from extracted data #
# Directory has been changed to spectral_maps/ #

def fit_sherpa(obsid_list, redshift, nH_Gal, energy, min_counts=25, kT_guess=3, Ab_guess=1, fix_nH_Gal=True, fix_abund=False, find_errors=True):

    spectra = []
    for obs in obsid_list:
        temp = glob.glob('xaf_*_' + obs + '.pi')  # get spectra of regions
        spectra.append(temp)  # spectra will be made of lists which have xaf_*_obs.pi filenames - access with spectra[i][j]
    spectra.sort()
    num_obs = len(obsid_list)
    num_reg = len(temp)
    filename = 'spectra_wabs_mekal.dat'
    results_file = open(filename, "w")
    results_file.write('# Fit results for wabs*mekal (zeros indicate that no fitting was performed)\n')
    results_file.write('# Reg_no.  kT  kT_loerr kT_hierr   Z    Z_loerr  Z_hierr  norm    norm_loerr norm_hierr nH_Gal  nH_loerr nH_hierr red_chisq total_counts num_bins\n')
    for i in range(num_reg):
        sherpa.clean()  # clean everything
        cnts = numpy.zeros(num_obs)  # make array of zeros with index length same as num_obs to store counts
        max_rate = numpy.zeros(num_obs)  # max count rate [counts/s/keV]
        data_set = 0  # data set number
        good_src_ids = numpy.zeros(num_obs, dtype=int) - 1

        for j in range(num_obs):
            sherpa.load_pha(data_set, spectra[j][i])  # load xaf_#_obs_####.pi and .arf and .rmf files.
            sherpa.ignore_id(data_set, 0.0, energy[0])
            sherpa.ignore_id(data_set, energy[1], None)
            cnts[j] = sherpa.calc_data_sum(energy[0], energy[1], data_set)
            cnt_rate = sherpa.get_rate(data_set, filter=True)
            if len(cnt_rate) == 0:
                max_rate[j] = 0.0  # when few counts (<50), get_rate can return zero-length array
            else:
                max_rate[j] = numpy.max(cnt_rate)
            sherpa.subtract(data_set)  # subtract background
            sherpa.set_source(data_set, sherpa.xswabs.abs1 * sherpa.xsmekal.plsm1)  # 1 temperature mekal model fit
            good_src_ids[j] = data_set
            data_set += 1  # same run for region but different obs

        # Filter out ignored obs
        good_src_ids_indx = numpy.where(good_src_ids >= 0)
        good_src_ids = good_src_ids[good_src_ids_indx]
        max_rate = max_rate[good_src_ids_indx]
        cnts = cnts[good_src_ids_indx]

        totcnts = numpy.sum(cnts)
        if totcnts >= min_counts:
            print('Fitting spectra in region: ' + str(i))
            abs1.nH = nH_Gal
            abs1.cache = 0
            if fix_nH_Gal:
                sherpa.freeze(abs1.nH)
            else:
                sherpa.thaw(abs1.nH)
            plsm1.kt = kT_guess
            sherpa.thaw(plsm1.kt)
            plsm1.Abundanc = Ab_guess
            if fix_abund:
                sherpa.freeze(plsm1.Abundanc)
            else:
                sherpa.thaw(plsm1.Abundanc)
            plsm1.redshift = redshift
            sherpa.freeze(plsm1.redshift)
            plsm1.cache = 0

            sherpa.fit()
            fit_result = sherpa.get_fit_results()
            red_chi2 = fit_result.rstat
            num_bins = fit_result.numpoints
            if fix_nH_Gal:
                nH = nH_Gal
                kT = fit_result.parvals[0]
                if fix_abund:
                    Z = Ab_guess
                    norm = fit_result.parvals[1]
                else:
                    Z = fit_result.parvals[1]
                    norm = fit_result.parvals[2]
            else:
                nH = fit_result.parvals[0]
                kT = fit_result.parvals[1]
                if fix_abund:
                    Z = Ab_guess
                    norm = fit_result.parvals[2]
                else:
                    Z = fit_result.parvals[2]
                    norm = fit_result.parvals[3]
            del fit_result

            if find_errors:
                sherpa.covar()
                covar_result = sherpa.get_covar_results()
                if fix_nH_Gal:
                    nH_loerr = 0.0
                    nH_hierr = 0.0
                    kT_loerr = covar_result.parmins[0]
                    kT_hierr = covar_result.parmaxes[0]
                    if fix_abund:
                        Z_loerr = 0.0
                        Z_hierr = 0.0
                        norm_loerr = covar_result.parmins[1]
                        norm_hierr = covar_result.parmaxes[1]
                    else:
                        Z_loerr = covar_result.parmins[1]
                        Z_hierr = covar_result.parmaxes[1]
                        norm_loerr = covar_result.parmins[2]
                        norm_hierr = covar_result.parmaxes[2]
                else:
                    nH_loerr = covar_result.parmins[0]
                    nH_hierr = covar_result.parmaxes[0]
                    kT_loerr = covar_result.parmins[1]
                    kT_hierr = covar_result.parmaxes[1]
                    if fix_abund:
                        Z_loerr = 0.0
                        Z_hierr = 0.0
                        norm_loerr = covar_result.parmins[2]
                        norm_hierr = covar_result.parmaxes[2]
                    else:
                        Z_loerr = covar_result.parmins[2]
                        Z_hierr = covar_result.parmaxes[2]
                        norm_loerr = covar_result.parmins[3]
                        norm_hierr = covar_result.parmaxes[3]
                del covar_result

                # Check for failed errors (= None) and set them to +/- best-fit value
                if not fix_nH_Gal:
                    if nH_loerr is None: nH_loerr = -nH  # is was ==
                    if nH_hierr is None: nH_hierr = nH
                if kT_loerr is None: kT_loerr = -kT
                if kT_hierr is None: kT_hierr = kT
                if not fix_abund:
                    if Z_loerr is None: Z_loerr = -Z
                    if Z_hierr is None: Z_hierr = Z
                if norm_loerr is None: norm_loerr = -norm
                if norm_hierr is None: norm_hierr = norm
            else:
                kT_loerr = 0.0
                Z_loerr = 0.0
                nH_loerr = 0.0
                norm_loerr = 0.0
                kT_hierr = 0.0
                Z_hierr = 0.0
                nH_hierr = 0.0
                norm_hierr = 0.0

        else:  # if total counts < min_counts, just write zeros
            print('\n Warning: no fit performed for for region: ' + str(i))
            print('\n Spectra have insufficient counts after filtering or do not exist.')
            print('\n --> All parameters for this region set to 0.0.')
            kT = 0.0
            Z = 0.0
            nH = 0.0
            norm = 0.0
            kT_loerr = 0.0
            Z_loerr = 0.0
            nH_loerr = 0.0
            norm_loerr = 0.0
            kT_hierr = 0.0
            Z_hierr = 0.0
            nH_hierr = 0.0
            norm_hierr = 0.0
            red_chi2 = 0.0
            num_bins = 0

        reg_id = spectra[0][i].split('_')  # Splits string after every underscore so that region number can be accessed. reg_id[1] is accessed because that is the region number after 'xaf'
        results_file.write('%7r %7.4f %7.4f %7.4f %7.4f %7.4f %7.4f %6.4e %6.4e %6.4e %7.4f %7.4f %7.4f %7.4f %8.1f %8r\n' % (int(reg_id[1]), kT, kT_loerr, kT_hierr, Z, Z_loerr, Z_hierr, norm, norm_loerr, norm_hierr, nH, nH_loerr, nH_hierr, red_chi2, totcnts, num_bins))  # Write all data to a file

    results_file.close()
