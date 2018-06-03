# Make directories for work #

import os


# Creating directories for work #

def mkdir():

    if os.path.exists('reprojected data'):
        pass
    else:
        os.system('mkdir reprojected_data')
    if os.path.exists('exposure_corrected_mosaic'):
        pass
    else:
        os.system('mkdir exposure_corrected_mosaic')
    if os.path.exists('blank_sky'):
        pass
    else:
        os.system('mkdir blank_sky')
    if os.path.exists('contbin'):
        pass
    else:
        os.system('mkdir contbin')
    if os.path.exists('spectral_maps'):
        pass
    else:
        os.system('mkdir spectral_maps')
    if os.path.exists('final_maps'):
        pass
    else:
        os.system('mkdir final_maps')
