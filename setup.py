#!/usr/bin/env python
# coding: utf-8


import re
from setuptools import setup, find_packages
from os import listdir
from os.path import isfile, join


exec(open('picopayments/version.py').read())  # load __version__


SQL_FILES = [
    "picopayments/sql/{0}".format(f) for f in listdir("picopayments/sql")
    if isfile(join("picopayments/sql", f)) and re.match(".*\.sql$", f)
]


setup(
    name='picopayments',
    scripts=['picopayments/bin/picopayments'],
    description="Micropayment hub for counterparty assets.",
    long_description=open("README.rst").read(),
    keywords="storj, counterparty, micropayment, hub",
    url='http://storj.io',
    author='Fabian Barkhau',
    author_email='f483@storj.io',
    license="MIT",
    version=__version__,  # NOQA
    test_suite="tests",
    dependency_links=[],
    data_files=SQL_FILES,
    install_requires=open("requirements.txt").readlines(),
    tests_require=open("test_requirements.txt").readlines(),
    packages=find_packages(),
    classifiers=[
        # "Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
