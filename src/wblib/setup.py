#!/usr/bin/env python
import os.path
from distutils.core import setup
from setuptools import find_packages

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(name='wblib',
      version=get_version("wblib/__init__.py"),   
      description='Weather Briefing library for PRECUSION',
      author='MPI-M',
      install_requires=["xarray", "netcdf4", "matplotlib", "cartopy"],
      packages=find_packages(),
      python_requires='>=3.10',
      classifiers=["Private :: Do Not Upload",
                   "License :: OSI Approved :: The 3-Clause BSD License (BSD-3-Clause)",
                   "Programming Language :: Python :: 3.10"]
     )
