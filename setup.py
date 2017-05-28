#!/usr/bin/env python

from setuptools import find_packages, setup
from nest.version import __version__


setup(
    name='drongo-nest',
    version=__version__,
    description='High performance server for drongo.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'uvloop==0.8.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
