#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='edge',
    version='0.1',
    description='Genome Engineering Tool',
    author='Ginkgo Bioworks',
    author_email='team@ginkgobioworks.com',
    long_description=open('README.md', 'r').read(),
    packages=['edge'],
    zip_safe=False,
    requires=[],
    install_requires=[
      'numpy',
      'biopython',
      'bcbio-gff==0.3',
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

