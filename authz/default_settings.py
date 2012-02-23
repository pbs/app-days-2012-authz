# -*- coding: utf-8 -*-
"""
    authz.default_settings
    ~~~~~~~~~~~~~~~~~~~~~~

    Default settings file for the authz application

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
# Enable / disable the debug mode
DEBUG = False


# Enable / disable the testing mode
TESTING = False


# Secret key to use for session cookies
SECRET_KEY = 'X9V.`O#+bQmTmvxsD_`0/>%m|XsC>Lh$t]lMY@rhI$R1P%hY^+m!g,H}oCm=7m@+'


# MongoAlchemy config
MONGOALCHEMY_SERVER = 'localhost'
MONGOALCHEMY_DATABASE = 'authz'
