#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import ( division, absolute_import, print_function, unicode_literals )
# import sys, os, tempfile, logging

from distutils.core import setup
from distutils.extension import Extension
import Cython
import Cython.Distutils
from Cython.Distutils import build_ext
import numpy
# import wget
import zipfile
import sys
import os
if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
    from urllib.error import URLError
else:
    import urllib2
    import urlparse
    from urllib2 import URLError

gco_directory = "gco_src"

files = ['GCoptimization.cpp', 'graph.cpp', 'LinkedBlockList.cpp',
         'maxflow.cpp']

files = [os.path.join(gco_directory, f) for f in files]
files.insert(0, "gco_python.pyx")

def download_file(url, dest=None, filename=None):
    """
    Download and save a file specified by url to dest directory,

    Inspired by:
    PabloG, Stan and Steve Barnes
    https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    """
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    if filename is None:
        filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if dest:
        filename = os.path.join(dest, filename)

    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        print("Downloading: {0} Bytes: {1}".format(url, file_size))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
            status += chr(13)
            # print(status, end="")
            print(status)


# download src files
# wget.download("http://vision.csd.uwo.ca/code/gco-v3.0.zip")
gco_zip = "gco-v3.0.zip"
if not os.path.exists(gco_zip):
    print("Downloading gco-v3.0.zip ...")
    try:
        download_file("http://home.zcu.cz/~mjirik/lisa/install/gco-v3.0.zip", filename=gco_zip)
    except URLError:
        print("Unable to reach home.zcu.cz")
        download_file("http://mouse.cs.uwaterloo.ca/code/gco-v3.0.zip", filename=gco_zip)

    # wget.download("http://home.zcu.cz/~mjirik/lisa/install/gco-v3.0.zip", out=gco_zip)
if not os.path.exists(gco_directory):
    os.makedirs(gco_directory)
if not os.path.exists(os.path.join(gco_directory, 'graph.h')):
    print("Unzipping gco-v3.0.zip into " + gco_directory)
    with zipfile.ZipFile(gco_zip) as zf:
        zf.extractall(gco_directory)


setup(
        
    name='pygco',
    description='Graph Cut for python',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.21',
    url='https://github.com/mjirik/gco_python',
    author='Andreas Mueller',
    author_email='',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("pygco", files, language="c++",
                            include_dirs=[gco_directory, numpy.get_include()],
                            library_dirs=[gco_directory],
                            extra_compile_args=["-fpermissive"])],
    package_data = {'': ['pygco.so']},
    install_requires=['cython'],
)
