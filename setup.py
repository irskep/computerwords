#!/usr/bin/env python

from setuptools import setup, find_packages


VERSION = '1.0a8'


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='computerwords',
    version=VERSION,

    description='A hopefully pretty good documentation system',
    long_description=readme(),
    license='BSD 3-clause',

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

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
    ],
)
