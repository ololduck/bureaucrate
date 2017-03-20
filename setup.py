#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

test_requirements = []

setup(
    name='bureaucrate',
    version='0.2.1',
    description="A maildir-based executer of rules, destined to sort and automate mail",
    long_description=readme + '\n\n' + history,
    author="Paul Ollivier",
    author_email='contact@paulollivier.fr',
    url='https://github.com/paulollivier/bureaucrate',
    packages=[
        'bureaucrate',
    ],
    package_dir={'bureaucrate':
                 'bureaucrate'},
    entry_points={},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='bureaucrate',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
