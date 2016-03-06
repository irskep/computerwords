#!/usr/bin/env python

from setuptools import setup, find_packages

reqs = [
    "CommonMark (>=0.6, <0.7)",
    "Pygments (>=2.1, <3.0)",
]

setup(
    name='Computer Words',
    version='0.5',
    description='A hopefully pretty good documentation system',
    author='Steve Johnson',
    author_email='steve@steveasleep.com',
    url='https://computerwords.net/',
    packages=find_packages(exclude=['tests.*']),
    include_package_data=True,
    requires=reqs,
    install_requires=reqs,
)