#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read().split('<!--- marker-for-pypi-to-trim --->')[0]

requirements = ['Click>=7.0', 'click_didyoumean', 'hangar @ git+https://github.com/hhsecond/hangar-py@dataset', 'rich']

setup(
    author="Sherin Thomas",
    author_email='sherin@tensorwerk.com',
    python_requires='>=3.6',
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
    description="Version control for software 2.0",
    project_urls={
        'Documentation': 'https://stockroom.readthedocs.io',
        'Issue Tracker': 'https://github.com/tensorwerk/stockroom/issues'},
    entry_points={'console_scripts': ['stock=stockroom.cli:stock']},
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n',
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='stockroom',
    name='stockroom',
    packages=find_packages(include=['stockroom', 'stockroom.*']),
    url='https://github.com/tensorwerk/stockroom',
    version='0.3.0',
    zip_safe=False,
)
