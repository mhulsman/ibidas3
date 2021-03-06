import sys

req_version = (2,6)
cur_version = sys.version_info

if not ((cur_version[0] > req_version[0]) or (cur_version[0] == req_version[0] and cur_version[1] >= req_version[1])):
    sys.stderr.write("Your python interpreter is too old. Ibidas needs at least Python 2.6. Please consider upgrading.\n")
    sys.exit(-1)

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup,find_packages,Extension
import distutils.sysconfig
import os
import os.path

#include_dir = distutils.sysconfig.get_python_lib() + "/numpy/core/include/"
#if(not os.path.isfile(os.path.join(include_dir, "numpy/arrayobject.h"))):
#    #print os.path.join(include_dir, "numpy/arrayobject.h")
#    include_dir = include_dir.replace('lib', 'lib64')
#    if(not os.path.isfile(os.path.join(include_dir, "numpy/arrayobject.h"))):
#        #print os.path.join(include_dir, "numpy/arrayobject.h")
#        raise RuntimeError('numpy array headers not found')

if not os.path.isdir('docs/_build'):
    os.mkdir('docs/_build')

setup(
    name="Ibidas3",
    version="0.2",
    packages = find_packages(),
    test_suite = "test",
    scripts = ['bin/ibidas3'],
     install_requires=['numpy>=1.4.1','numpy!=1.6.0','ipython','spark-parser','sqlalchemy'],
     author = "M. Hulsman & J.J.Bot",
     author_email = "m.hulsman@tudelft.nl",
     description = "Ibidas is an environment for data handling and exploration, able to cope with different data structures and sources",
     url = "https://trac.nbic.nl/ibidas/",
     license = "LGPLv2.1",

)

