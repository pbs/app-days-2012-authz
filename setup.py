#!/usr/bin/env python
import os
from setuptools import setup, find_packages


"""The path to the README file."""
README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'README.rst')


"""The list of dependencies for this package."""
dependencies = (
    # Framework dependencies
    'Flask==0.8.0',
    'Flask-Admin==0.3.0',

    # MongoDB dependencies
    'PyMongo==2.5.2',
    'MongoAlchemy==0.11',
    'Flask-MongoAlchemy==0.5.3',

    # OpenID dependencies
    'python-openid==2.2.5',
    'Flask-OpenID==1.0.1',

    # OAuth dependencies
    'httplib2==0.7.2',
    'oauth2==1.5.166',

    # Other dependencies
    'wtforms==0.6.3',
)


dependency_links = (
    'https://github.com/zyegfryed/python-oauth2/tarball/master#egg=oauth2-1.5.166',
)


"""Setup entry for the package."""
setup(
    name='authz',
    version='0.1.2',
    description='',
    long_description=open(README_PATH, 'r').read(),
    author='Ion Scerbatiuc',
    author_email='authz@pbs.org',
    url='http://authz.pbs.org/',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['s3sourceuploader',],
    install_requires=dependencies,
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'runserver = authz.web:runserver',
            'createadmin = authz.admin.auth:create_admin'
        ]
    },
    test_suite='authz',
)
