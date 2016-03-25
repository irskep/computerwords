#!/usr/bin/env python

from setuptools import setup, find_packages


VERSION = '1.0a1'


setup(
    name='computerwords',
    version=VERSION,
    description='A hopefully pretty good documentation system',
    author='Steve Johnson',
    author_email='steve@steveasleep.com',
    url='https://steveasleep.com/computerwords/',
    packages=find_packages(exclude=['tests.*']),
    include_package_data=True,
    requires=[
        "CommonMark (>=0.6, <0.7)",
        "Pygments (>=2.1, <3.0)",
    ],
    install_requires=[
        "CommonMark>=0.6,<0.7",
        "Pygments>=2.1,<3.0",
    ],

    download_url='https://github.com/irskep/computerwords/tarball/' + VERSION,
    keywords=['documentation', 'docs', 'markdown'],
)
