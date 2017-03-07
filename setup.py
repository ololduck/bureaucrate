#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='bureaucrate',
    version='0.1.0',
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
    entry_points={
        'console_scripts': [
            'bureaucrate=bureaucrate.cli:main'
        ]
    },
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
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
