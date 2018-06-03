try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A Python module to make X-ray Spectral maps of Temperature, Density, and Entropy for Chandra Observations of Galaxy Clusters',
    'author': 'Grant R. Tremblay & Dominic E. Eggerman',
    'url': 'https://github.com/dominiceggerman/Argos',
    'download_url': 'https://github.com/dominiceggerman/Argos',
    'author_email': 'dominiceggerman@gmail.com',
    'version': '0.1dev',
    'install_requires': ['nose','CIAO'],
    'packages': ['Argos'],
    'scripts': [],
    'name': 'Argos'
}

setup(**config)