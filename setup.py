#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Computer Words',
    version='0.5',
    description='A hopefully pretty good documentation system',
    author='Steve Johnson',
    author_email='steve@steveasleep.com',
    url='https://computerwords.net/',
    packages=['computerwords'],
    requires=[
        "CommonMark (>=0.6, <0.7)",
    ],
)