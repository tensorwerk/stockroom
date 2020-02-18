#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'hangar>=0.4.0']

setup(
    author="Sherin Thomas",
    author_email='sherin@tensorwerk.com',
    python_requires='>=3.6',
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A hangar wrapper that enables the versioning of model, params "
                "and metrics along with data",
    entry_points={
        'console_scripts': [
            'stock=stockroom.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='stockroom',
    name='stockroom',
    packages=find_packages(include=['stockroom', 'stockroom.*']),
    url='https://github.com/tensorwerk/stockroom',
    version='0.1.0',
    zip_safe=False,
)
