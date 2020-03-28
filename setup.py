#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lr2irscraper',
    version='2.1',
    description='LR2 Internet Ranking Scraper Library',
    author='nakt',
    author_email='nakt_azdim@walkure.net',
    install_requires=['pandas>=0.21', 'requests', 'lxml'],
    python_requires='>=3.7',
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests'
)
