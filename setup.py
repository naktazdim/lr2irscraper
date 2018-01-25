#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lr2irscraper',
    version='0.1',
    description='LR2 Internet Ranking Scraper Library',
    author='nakt',
    author_email='nakt_azdim@walkure.net',
    install_requires=['pandas', 'pyjsparser'],
    python_requires='>=3.5',
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests'
)
