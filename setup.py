from setuptools import setup, find_packages
from distutils.core import Extension

DISTNAME = 'mexnets'
VERSION = '0.9'
PACKAGES = find_packages()
EXTENSIONS = []
DESCRIPTION = 'Package for mass exchanger network synthesis'
LONG_DESCRIPTION = '' #open('README.md').read()
AUTHOR = 'Michael Short'
MAINTAINER_EMAIL = 'shortm@andrew.cmu.edu'
LICENSE = 'GPL-3'
URL = 'https://github.com/mchlshort/mexnets'

setuptools_kwargs = {
    'zip_safe': False,
    'install_requires': ['six',
                         'pyomo>=5.5',
                         'numpy',
                         'scipy',
                         'pandas'],
    'scripts': [],
    'include_package_data': True
}

setup(name=DISTNAME,
      version=VERSION,
      packages=PACKAGES,
      ext_modules=EXTENSIONS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      **setuptools_kwargs)
