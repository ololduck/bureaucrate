#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


setup(
    name='bureaucrate',
    version='0.3.8',
    description="A maildir-based executer of rules, destined to sort and "
                "automate mail",
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
            'bureaucrate=bureaucrate.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='bureaucrate',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Environment :: Console',
        'Topic :: Communications :: Email :: Filters',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
