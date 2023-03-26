#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2023 KCC project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@firmwaretoolkit.org
#

from kcc.release import __version__, __author__, __author_email__

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

config = {
    'description': 'Kernel Config File Comparator',

    'long_description': 'KCC is a tool designed to execute comparisons and basic operations on Linux kernel config files. KCC can produce associated fragments accondring to the operation given as argument. The fragment will later be used with the merge_config.sh script from kernel sources',
    'author': __author__,
    'url': 'https://github.com/canuckbear/kcc/',
    'download_url': 'https://github.com/canuckbear/kcc/',
    'author_email': __author_email__,
    'version': __version__,
    'install_requires': [ 'pyyaml' ],
    'packages': ['kcc'],
    'scripts': [ 'bin/kcc' ],
    'name': 'kcc'
}

setup(**config)
